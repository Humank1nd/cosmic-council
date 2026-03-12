"""
Example integration of Agent Interactions API into main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the agent interactions router
from .agent_interactions import router as agent_router, initialize_agents

# Import the main Agent Orchestrator components
from ..core.hexagon import CosmicCouncilHexagon
from ..core.api import app as main_app  # If you have a main API app

# Option 1: Create a new FastAPI app and include the router
def create_app_with_agent_api():
    """Create FastAPI app with agent interactions API"""
    app = FastAPI(
        title="Agent Orchestrator API with Agent Interactions",
        description="Enhanced API with agent interaction endpoints",
        version="1.1.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize the council and agents
    council = CosmicCouncilHexagon()
    initialize_agents(council)
    
    # Include the agent interactions router
    app.include_router(agent_router)
    
    return app


# Option 2: Add to existing FastAPI app
def add_agent_api_to_existing_app(app: FastAPI, council: CosmicCouncilHexagon = None):
    """Add agent interactions API to an existing FastAPI app"""
    # Initialize agents with council instance
    if council is None:
        council = CosmicCouncilHexagon()
    
    initialize_agents(council)
    
    # Include the router
    app.include_router(agent_router)
    
    return app


# Example usage in main.py or startup
if __name__ == "__main__":
    # Create app
    app = create_app_with_agent_api()
    
    # Run with uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

