#!/usr/bin/env python3
"""
Cosmic Council MVP - Production Entry Point
Supports both CLI and API modes with proper configuration.
"""

import sys
import argparse
from pathlib import Path
import asyncio
import os

sys.path.insert(0, str(Path(__file__).parent))

from cosmic_council import CosmicCouncilMVP
from cosmic_council.database import SimpleDatabase
from cosmic_council.database_improved import ProductionDatabase, DatabaseConfig
from cosmic_council.config import get_config, initialize_config
from cosmic_council.logging_config import setup_logging
from cosmic_council.api import run_api


def main():
    """Main entry point for the Cosmic Council MVP."""
    parser = argparse.ArgumentParser(
        description="Cosmic Council MVP - Production AI-Powered Problem-Solving Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CLI Mode
  python main_production.py "How do I improve team productivity?"
  python main_production.py --interactive
  python main_production.py --test
  python main_production.py --demo
  
  # API Mode
  python main_production.py --api
  python main_production.py --api --host 0.0.0.0 --port 8080
  
  # Configuration
  python main_production.py --config config.json
  python main_production.py --env-file .env
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        'problem',
        nargs='?',
        help='The problem to solve (CLI mode)'
    )
    mode_group.add_argument(
        '--api',
        action='store_true',
        help='Run in API mode'
    )
    mode_group.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    mode_group.add_argument(
        '--test',
        action='store_true',
        help='Run the MVP tests'
    )
    mode_group.add_argument(
        '--demo',
        action='store_true',
        help='Run a demo problem'
    )
    
    # Configuration options
    parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    parser.add_argument(
        '--env-file',
        help='Environment file path'
    )
    parser.add_argument(
        '--database',
        help='Database file path'
    )
    
    # API options
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='API host (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API port (default: 8000)'
    )
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level override'
    )
    parser.add_argument(
        '--log-file',
        help='Log file path'
    )
    
    args = parser.parse_args()
    
    try:
        # Load environment file if specified
        if args.env_file:
            from dotenv import load_dotenv
            load_dotenv(args.env_file)
        
        # Initialize configuration
        if args.config:
            config = initialize_config(args.config, from_env=False)
        else:
            config = initialize_config(from_env=True)
        
        # Override configuration with command line arguments
        if args.database:
            config.database.db_path = args.database
        if args.log_level:
            from cosmic_council.config import LogLevel
            config.logging.level = LogLevel(args.log_level)
        if args.log_file:
            config.logging.file_path = args.log_file
        
        # Setup logging
        loggers = setup_logging(config.logging)
        app_logger = loggers['app']
        
        app_logger.info("🚀 Cosmic Council MVP starting...")
        app_logger.info(f"Mode: {'API' if args.api else 'CLI'}")
        app_logger.info(f"Environment: {config.environment}")
        app_logger.info(f"Debug mode: {config.debug_mode}")
        
        # Route to appropriate mode
        if args.api:
            run_api_mode(args, config, app_logger)
        elif args.test:
            run_tests(config, app_logger)
        elif args.demo:
            run_demo(config, app_logger)
        elif args.interactive:
            run_interactive_mode(config, app_logger)
        elif args.problem:
            solve_problem(args.problem, config, app_logger)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'app_logger' in locals():
            app_logger.error(f"Application error: {e}")
        sys.exit(1)


def run_api_mode(args, config, logger):
    """Run the API server."""
    logger.info(f"🌐 Starting API server on {args.host}:{args.port}")
    
    # Set environment variables for the API
    os.environ['API_HOST'] = args.host
    os.environ['API_PORT'] = str(args.port)
    os.environ['API_RELOAD'] = str(args.reload)
    
    # Run the API
    run_api(host=args.host, port=args.port, reload=args.reload)


def solve_problem(problem: str, config, logger):
    """Solve a specific problem using production database."""
    logger.info(f"🎯 Solving problem: {problem[:100]}...")
    
    # Initialize the council
    council = CosmicCouncilMVP()
    
    # Initialize production database
    db_config = DatabaseConfig(
        db_path=config.database.db_path,
        pool_size=config.database.pool_size,
        timeout=config.database.timeout
    )
    db = ProductionDatabase(db_config)
    
    try:
        # Save problem to database
        problem_id = db.save_problem(problem)
        
        # Solve the problem
        results = council.solve_problem_sync(problem)
        
        # Save solutions to database
        for enterprise_name, solution_text in results.items():
            db.save_solution(problem_id, enterprise_name, solution_text)
        
        # Save problem session
        db.save_problem_session(problem_id, results)
        
        # Display results
        print("🚀 Cosmic Council MVP - Problem Solver")
        print("=" * 50)
        print(f"🎯 Problem: {problem}")
        print()
        
        for enterprise, solution in results.items():
            print(f"{solution}")
            print()
        
        # Show database stats
        try:
            stats = db.get_database_stats()
            print("📊 Database Stats:")
            print(f"  Problems: {stats.get('problems', 0)}")
            print(f"  Solutions: {stats.get('solutions', 0)}")
            print(f"  Sessions: {stats.get('sessions', 0)}")
            print(f"  Average Confidence: {stats.get('average_confidence', 0):.1%}")
            print(f"  Total Cost: ${stats.get('total_cost', 0):.4f}")
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            print("📊 Database Stats: Unable to retrieve")
        
        print("\n🎉 Problem solving complete!")
        
    finally:
        db.close()


def run_interactive_mode(config, logger):
    """Run in interactive mode with production database."""
    logger.info("🔄 Starting interactive mode")
    
    print("🚀 Cosmic Council MVP - Interactive Mode")
    print("=" * 50)
    print("Enter problems to solve. Type 'quit' to exit.")
    print()
    
    # Initialize the council
    council = CosmicCouncilMVP()
    
    # Initialize production database
    db_config = DatabaseConfig(
        db_path=config.database.db_path,
        pool_size=config.database.pool_size,
        timeout=config.database.timeout
    )
    db = ProductionDatabase(db_config)
    
    try:
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
                logger.error(f"Error in interactive mode: {e}")
                print(f"❌ Error: {e}")
                print()
    
    finally:
        db.close()


def run_demo(config, logger):
    """Run a demo with production database."""
    logger.info("🎬 Starting demo mode")
    
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
    
    # Initialize production database
    db_config = DatabaseConfig(
        db_path="demo_production.db",
        pool_size=config.database.pool_size,
        timeout=config.database.timeout
    )
    db = ProductionDatabase(db_config)
    
    try:
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
        print(f"  Average Confidence: {stats['average_confidence']:.1%}")
        print(f"  Total Cost: ${stats['total_cost']:.4f}")
        
        print("\n🎉 Demo complete!")
    
    finally:
        db.close()


def run_tests(config, logger):
    """Run the MVP tests."""
    logger.info("🧪 Running tests")
    
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
