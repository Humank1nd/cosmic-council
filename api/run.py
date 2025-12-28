#!/usr/bin/env python3
"""
Cosmic Council API Server Runner
"""
import sys
import os
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="Cosmic Council API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    print("""
+===========================================================================+
|                         COSMIC COUNCIL API                                |
|             Six Enterprises - Collective Problem Solving                  |
+===========================================================================+
|                                                                           |
|    [RED OWL]        WHY?    - Knowledge & Research                       |
|    [ORANGE ORANGUTAN] HOW?  - Logistics & Planning                       |
|    [YELLOW HONEYBEE]  WHAT? - Prototype & Development                    |
|    [GREEN TORTOISE]   WHEN? - Resources & Timing                         |
|    [BLUE DOLPHIN]     WHERE? - Communication & Distribution              |
|    [PURPLE ELEPHANT]  WHO?  - Empathy & Stakeholders                     |
|                                                                           |
|    Flow: Red -> Orange -> Yellow -> Green -> Blue -> Purple              |
|                                                                           |
+===========================================================================+
    """)

    print(f"Starting Cosmic Council API on http://{args.host}:{args.port}")
    print(f"API docs: http://localhost:{args.port}/docs")
    print()

    import uvicorn
    uvicorn.run(
        "src.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
