"""
Cosmic Council Web Interface
Modern web interface with consistent UI theme matching other game UIs
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our existing components
from src.api.main import app as api_app
from api_client import CosmicCouncilAPIClient, APIException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application for web interface
app = FastAPI(
    title="Cosmic Council Web Interface",
    description="Modern web interface for the Cosmic Council problem-solving framework",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(templates_dir))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_sessions[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")

    async def send_to_user(self, message: str, user_id: str):
        if user_id in self.user_sessions:
            await self.send_personal_message(message, self.user_sessions[user_id])

manager = ConnectionManager()

# Pydantic models for web interface
class ProblemFormData(BaseModel):
    title: str
    description: str
    domain: str
    complexity: str
    priority: str = "medium"
    stakeholders: List[str] = []
    constraints: Dict[str, Any] = {}
    success_criteria: List[str] = []

class CycleFormData(BaseModel):
    problem_id: str
    cycle_number: int = 1
    max_iterations: int = 3

class SolutionFormData(BaseModel):
    problem_id: str
    cycle_id: str
    title: str
    description: str
    approach: Optional[str] = None
    confidence_score: Optional[float] = None
    feasibility_score: Optional[float] = None
    impact_score: Optional[float] = None
    estimated_cost: Optional[float] = None
    estimated_duration: Optional[int] = None
    risk_level: Optional[str] = None

# Web interface routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with dashboard overview"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Cosmic Council - Problem Solving Framework",
        "page": "home"
    })

@app.get("/problems", response_class=HTMLResponse)
async def problems_page(request: Request):
    """Problems management page"""
    return templates.TemplateResponse("problems.html", {
        "request": request,
        "title": "Problems - Cosmic Council",
        "page": "problems"
    })

@app.get("/cycles", response_class=HTMLResponse)
async def cycles_page(request: Request):
    """Cycles management page"""
    return templates.TemplateResponse("cycles.html", {
        "request": request,
        "title": "Cycles - Cosmic Council",
        "page": "cycles"
    })

@app.get("/solutions", response_class=HTMLResponse)
async def solutions_page(request: Request):
    """Solutions management page"""
    return templates.TemplateResponse("solutions.html", {
        "request": request,
        "title": "Solutions - Cosmic Council",
        "page": "solutions"
    })

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "title": "Analytics - Cosmic Council",
        "page": "analytics"
    })

@app.get("/workflow", response_class=HTMLResponse)
async def workflow_page(request: Request):
    """Interactive workflow page"""
    return templates.TemplateResponse("workflow.html", {
        "request": request,
        "title": "Workflow - Cosmic Council",
        "page": "workflow"
    })

@app.get("/hexagon", response_class=HTMLResponse)
async def hexagon_page(request: Request):
    """Interactive hexagon visualization page"""
    return templates.TemplateResponse("hexagon.html", {
        "request": request,
        "title": "Hexagon Visualization - Cosmic Council",
        "page": "hexagon"
    })

@app.get("/perpetual", response_class=HTMLResponse)
async def perpetual_page(request: Request):
    """Perpetual thinking engine page"""
    return templates.TemplateResponse("perpetual.html", {
        "request": request,
        "title": "Perpetual Thinking - Cosmic Council",
        "page": "perpetual"
    })

# API proxy endpoints for web interface

@app.post("/api/web/problems")
async def create_problem_web(data: ProblemFormData):
    """Create a problem via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.create_problem(
                title=data.title,
                description=data.description,
                domain=data.domain,
                complexity=data.complexity,
                priority=data.priority,
                stakeholders=data.stakeholders,
                constraints=data.constraints,
                success_criteria=data.success_criteria
            )
            
            # Broadcast to all connected clients
            await manager.broadcast(json.dumps({
                "type": "problem_created",
                "data": result["data"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating problem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/problems")
async def get_problems_web(
    domain: Optional[str] = None,
    complexity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get problems via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.get_problems(
                domain=domain,
                complexity=complexity,
                status=status,
                limit=limit,
                offset=offset
            )
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting problems: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/web/cycles")
async def create_cycle_web(data: CycleFormData):
    """Create a cycle via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.create_cycle(
                problem_id=data.problem_id,
                cycle_number=data.cycle_number,
                max_iterations=data.max_iterations
            )
            
            # Broadcast to all connected clients
            await manager.broadcast(json.dumps({
                "type": "cycle_created",
                "data": result["data"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating cycle: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/web/cycles/{cycle_id}/execute")
async def execute_cycle_web(cycle_id: str):
    """Execute a cycle via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.execute_cycle(cycle_id)
            
            # Broadcast to all connected clients
            await manager.broadcast(json.dumps({
                "type": "cycle_execution_started",
                "data": result["data"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing cycle: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/web/solutions")
async def create_solution_web(data: SolutionFormData):
    """Create a solution via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.create_solution(
                problem_id=data.problem_id,
                cycle_id=data.cycle_id,
                title=data.title,
                description=data.description,
                approach=data.approach,
                confidence_score=data.confidence_score,
                feasibility_score=data.feasibility_score,
                impact_score=data.impact_score,
                estimated_cost=data.estimated_cost,
                estimated_duration=data.estimated_duration,
                risk_level=data.risk_level
            )
            
            # Broadcast to all connected clients
            await manager.broadcast(json.dumps({
                "type": "solution_created",
                "data": result["data"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/analytics")
async def get_analytics_web():
    """Get analytics via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            problem_analytics = await client.get_problem_analytics()
            cycle_analytics = await client.get_cycle_analytics()
            solution_analytics = await client.get_solution_analytics()
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "problems": problem_analytics["data"],
                    "cycles": cycle_analytics["data"],
                    "solutions": solution_analytics["data"]
                }
            })
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/enterprises")
async def get_enterprises_web():
    """Get enterprises via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.get_enterprises()
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting enterprises: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Perpetual Thinking API proxy endpoints

@app.post("/api/web/perpetual/sessions")
async def create_perpetual_session_web(data: dict):
    """Create a perpetual thinking session via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.create_perpetual_session(
                session_name=data.get("session_name"),
                initial_input=data.get("initial_input"),
                mode=data.get("mode", "collaborative"),
                goals=data.get("goals", []),
                success_criteria=data.get("success_criteria", []),
                ai_enhancement_level=data.get("ai_enhancement_level", "enhanced"),
                ai_learning_enabled=data.get("ai_learning_enabled", True),
                ai_adaptation_enabled=data.get("ai_adaptation_enabled", True),
                ai_breakthrough_detection=data.get("ai_breakthrough_detection", True)
            )
            
            # Broadcast to all connected clients
            await manager.broadcast(json.dumps({
                "type": "perpetual_session_created",
                "data": result["data"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating perpetual session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/perpetual/sessions")
async def get_perpetual_sessions_web(
    status: Optional[str] = None,
    limit: int = 50
):
    """Get perpetual thinking sessions via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.get_perpetual_sessions(
                status=status,
                limit=limit
            )
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting perpetual sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/perpetual/status")
async def get_perpetual_status_web():
    """Get perpetual thinking system status via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.get_perpetual_system_status()
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting perpetual status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/perpetual/ai/sessions")
async def get_ai_sessions_web(
    ai_enhancement_level: Optional[str] = None,
    limit: int = 50
):
    """Get AI-enhanced sessions via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.get_ai_sessions(
                ai_enhancement_level=ai_enhancement_level,
                limit=limit
            )
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting AI sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/web/perpetual/ai/sessions/{session_id}/analytics")
async def get_ai_session_analytics_web(session_id: str):
    """Get AI session analytics via web interface"""
    try:
        async with CosmicCouncilAPIClient() as client:
            result = await client.get_ai_session_analytics(session_id)
            return JSONResponse(content=result)
            
    except APIException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting AI session analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    user_id = f"user_{datetime.now().timestamp()}"
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }), websocket)
            elif message.get("type") == "subscribe":
                # Handle subscription to specific updates
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, user_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "cosmic-council-web-interface"
    })

# Main execution
if __name__ == "__main__":
    uvicorn.run(
        "web_interface:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
