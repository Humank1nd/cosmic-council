"""
Main application entry point for the Cosmic Council system.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from .api.main import create_app
from .agents.orchestration.coordinator import AgentCoordinator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global coordinator instance
coordinator: AgentCoordinator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global coordinator
    
    # Startup
    logger.info("Starting Cosmic Council application...")
    
    try:
        # Initialize agent coordinator
        coordinator = AgentCoordinator()
        logger.info("Agent coordinator initialized successfully")
        
        # Start message processing
        asyncio.create_task(coordinator.communication_hub.process_messages())
        logger.info("Message processing started")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Cosmic Council application...")


def create_application() -> FastAPI:
    """Create the main application"""
    app = create_app()
    app.router.lifespan_context = lifespan
    return app


def get_coordinator() -> AgentCoordinator:
    """Get the global coordinator instance"""
    return coordinator


if __name__ == "__main__":
    app = create_application()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
