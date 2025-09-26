#!/usr/bin/env python3
"""
Cosmic Council Framework - Main Entry Point
The Ultimate Problem-Solving Framework

Usage:
    python main.py                    # Start web interface
    python main.py --demo             # Run demo
    python main.py --api              # Start API server
    python main.py --help             # Show help
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(
        description="Cosmic Council Framework - The Ultimate Problem-Solving Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start web interface
  python main.py --demo             # Run interactive demo
  python main.py --api              # Start API server
  python main.py --workflow         # Start workflow interface
        """
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true', 
        help='Run the interactive demo'
    )
    
    parser.add_argument(
        '--api', 
        action='store_true', 
        help='Start the API server'
    )
    
    parser.add_argument(
        '--workflow', 
        action='store_true', 
        help='Start the workflow interface'
    )
    
    parser.add_argument(
        '--web', 
        action='store_true', 
        help='Start the web interface (default)'
    )
    
    args = parser.parse_args()
    
    # Default to web interface if no specific option is chosen
    if not any([args.demo, args.api, args.workflow]):
        args.web = True
    
    try:
        if args.demo:
            print("🚀 Starting Cosmic Council Demo...")
            from examples.demo_cosmic_council import main as demo_main
            asyncio.run(demo_main())
            
        elif args.api:
            print("🚀 Starting Cosmic Council API Server...")
            from src.cosmic_council.core.api import main as api_main
            api_main()
            
        elif args.workflow:
            print("🚀 Starting Cosmic Council Workflow Interface...")
            from src.cosmic_council.workflows.interactive_workflow_interface import main as workflow_main
            workflow_main()
            
        elif args.web:
            print("🚀 Starting Cosmic Council Web Interface...")
            from src.cosmic_council.web.web_interface import main as web_main
            web_main()
            
    except ImportError as e:
        print(f"❌ Error: Could not import required module: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
