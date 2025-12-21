"""
Hexagon Web Server for Cosmic Council Visualization
Serves the interactive hexagon visualization with real-time updates
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import Cosmic Council components
from src.core.types import (
    CosmicCouncil, ProblemStatement, ProblemComplexity, 
    EnterpriseType, CycleStatus
)
from working_enhanced_agents import (
    WorkingEnhancedRedOwlAgent, WorkingEnhancedOrangeOrangutanAgent,
    AnalysisDepth
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualizationState:
    """Current state of the visualization"""
    problem: Optional[Dict[str, Any]] = None
    sector_states: Dict[str, Dict[str, Any]] = None
    cycle_in_progress: bool = False
    last_update: datetime = None
    
    def __post_init__(self):
        if self.sector_states is None:
            self.sector_states = {}
        if self.last_update is None:
            self.last_update = datetime.now(timezone.utc)

class HexagonWebServer:
    """Web server for the hexagon visualization"""
    
    def __init__(self):
        self.app = FastAPI(title="Cosmic Council Hexagon Visualization", version="1.0.0")
        self.council = CosmicCouncil()
        self.visualization_state = VisualizationState()
        self.connected_clients: List[WebSocket] = []
        self.enterprise_agents = {
            EnterpriseType.RED_OWL: WorkingEnhancedRedOwlAgent(AnalysisDepth.COMPREHENSIVE),
            EnterpriseType.ORANGE_ORANGUTAN: WorkingEnhancedOrangeOrangutanAgent(AnalysisDepth.COMPREHENSIVE)
        }
        
        # Enterprise configuration
        self.enterprise_config = {
            "red-owl": {"name": "Red Owl", "animal": "Owl", "principle": "Curiosity", "role": "Research & Inquiry"},
            "orange-orangutan": {"name": "Orange Orangutan", "animal": "Orangutan", "principle": "Planning", "role": "Logistics & Strategy"},
            "yellow-honeybee": {"name": "Yellow Honeybee", "animal": "Honeybee", "principle": "Creativity", "role": "Development & Innovation"},
            "green-tortoise": {"name": "Green Tortoise", "animal": "Tortoise", "principle": "Sustainability", "role": "Budget & Resources"},
            "blue-dolphin": {"name": "Blue Dolphin", "animal": "Dolphin", "principle": "Clarity", "role": "Communication & Marketing"},
            "purple-elephant": {"name": "Purple Elephant", "animal": "Elephant", "principle": "Empathy", "role": "Support & Feedback"}
        }
        
        self._setup_routes()
        self._setup_middleware()
        self._initialize_sector_states()
    
    def _setup_middleware(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def serve_visualization():
            """Serve the main visualization page"""
            return FileResponse("web_hexagon_visualization.html")
        
        @self.app.get("/api/supra_enterprise")
        async def get_enterprises():
            """Get enterprise configuration"""
            return {"enterprises": self.enterprise_config}
        
        @self.app.get("/api/state")
        async def get_state():
            """Get current visualization state"""
            return asdict(self.visualization_state)
        
        @self.app.post("/api/problem")
        async def set_problem(problem_data: Dict[str, Any]):
            """Set the current problem"""
            try:
                # Create ProblemStatement from data
                problem = ProblemStatement(
                    title=problem_data.get("title", ""),
                    description=problem_data.get("description", ""),
                    complexity=ProblemComplexity(problem_data.get("complexity", "moderate")),
                    domain=problem_data.get("domain", ""),
                    stakeholders=problem_data.get("stakeholders", []),
                    constraints=problem_data.get("constraints", {}),
                    success_criteria=problem_data.get("success_criteria", [])
                )
                
                self.visualization_state.problem = {
                    "title": problem.title,
                    "description": problem.description,
                    "complexity": problem.complexity.value,
                    "domain": problem.domain,
                    "stakeholders": problem.stakeholders,
                    "constraints": problem.constraints,
                    "success_criteria": problem.success_criteria
                }
                
                self.visualization_state.last_update = datetime.now(timezone.utc)
                
                # Broadcast update to connected clients
                await self._broadcast_update("problem_set", self.visualization_state.problem)
                
                return {"status": "success", "problem": self.visualization_state.problem}
                
            except Exception as e:
                logger.error(f"Error setting problem: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/api/sector/{enterprise}/toggle")
        async def toggle_sector(enterprise: str):
            """Toggle a sector's state"""
            if enterprise not in self.enterprise_config:
                raise HTTPException(status_code=404, detail="Enterprise not found")
            
            if self.visualization_state.cycle_in_progress:
                raise HTTPException(status_code=400, detail="Cannot toggle during cycle")
            
            current_state = self.visualization_state.sector_states.get(enterprise, {}).get("state", "inactive")
            new_state = "active" if current_state == "inactive" else "inactive"
            
            self.visualization_state.sector_states[enterprise] = {
                "state": new_state,
                "progress": 0,
                "confidence": 0,
                "last_update": datetime.now(timezone.utc).isoformat()
            }
            
            self.visualization_state.last_update = datetime.now(timezone.utc)
            
            # Broadcast update
            await self._broadcast_update("sector_toggled", {
                "enterprise": enterprise,
                "state": new_state
            })
            
            return {"status": "success", "enterprise": enterprise, "state": new_state}
        
        @self.app.post("/api/cycle/start")
        async def start_cycle():
            """Start a problem-solving cycle"""
            if self.visualization_state.cycle_in_progress:
                raise HTTPException(status_code=400, detail="Cycle already in progress")
            
            if not self.visualization_state.problem:
                raise HTTPException(status_code=400, detail="No problem set")
            
            # Start cycle in background
            cycle_thread = threading.Thread(target=self._run_cycle_background)
            cycle_thread.daemon = True
            cycle_thread.start()
            
            return {"status": "success", "message": "Cycle started"}
        
        @self.app.post("/api/cycle/reset")
        async def reset_cycle():
            """Reset the visualization"""
            if self.visualization_state.cycle_in_progress:
                raise HTTPException(status_code=400, detail="Cannot reset during cycle")
            
            self._initialize_sector_states()
            self.visualization_state.last_update = datetime.now(timezone.utc)
            
            # Broadcast update
            await self._broadcast_update("cycle_reset", {})
            
            return {"status": "success", "message": "Visualization reset"}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.connected_clients.append(websocket)
            
            try:
                # Send current state to new client
                await websocket.send_text(json.dumps({
                    "type": "state_update",
                    "data": asdict(self.visualization_state)
                }))
                
                # Keep connection alive
                while True:
                    data = await websocket.receive_text()
                    # Handle client messages if needed
                    
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
                logger.info("Client disconnected")
    
    def _initialize_sector_states(self):
        """Initialize sector states"""
        for enterprise in self.enterprise_config.keys():
            self.visualization_state.sector_states[enterprise] = {
                "state": "inactive",
                "progress": 0,
                "confidence": 0,
                "last_update": datetime.now(timezone.utc).isoformat()
            }
    
    async def _broadcast_update(self, update_type: str, data: Any):
        """Broadcast update to all connected clients"""
        message = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        message_text = json.dumps(message)
        disconnected_clients = []
        
        for client in self.connected_clients:
            try:
                await client.send_text(message_text)
            except:
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.connected_clients.remove(client)
    
    def _run_cycle_background(self):
        """Run the problem-solving cycle in background"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._execute_cycle())
        loop.close()
    
    async def _execute_cycle(self):
        """Execute the problem-solving cycle"""
        self.visualization_state.cycle_in_progress = True
        
        try:
            # Create ProblemStatement from current state
            problem_data = self.visualization_state.problem
            problem = ProblemStatement(
                title=problem_data["title"],
                description=problem_data["description"],
                complexity=ProblemComplexity(problem_data["complexity"]),
                domain=problem_data["domain"],
                stakeholders=problem_data["stakeholders"],
                constraints=problem_data["constraints"],
                success_criteria=problem_data["success_criteria"]
            )
            
            # Processing order
            processing_order = [
                "red-owl",
                "orange-orangutan",
                "yellow-honeybee", 
                "green-tortoise",
                "blue-dolphin",
                "purple-elephant"
            ]
            
            # Process each enterprise
            for i, enterprise in enumerate(processing_order):
                # Set to processing
                self.visualization_state.sector_states[enterprise] = {
                    "state": "processing",
                    "progress": 0,
                    "confidence": 0,
                    "last_update": datetime.now(timezone.utc).isoformat()
                }
                
                await self._broadcast_update("sector_processing", {
                    "enterprise": enterprise,
                    "progress": 0
                })
                
                # Simulate processing with progress updates
                for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
                    await asyncio.sleep(1.0)  # Simulate processing time
                    
                    self.visualization_state.sector_states[enterprise]["progress"] = progress
                    await self._broadcast_update("sector_progress", {
                        "enterprise": enterprise,
                        "progress": progress
                    })
                
                # Simulate completion with confidence score
                confidence = 0.7 + (i * 0.05)
                self.visualization_state.sector_states[enterprise] = {
                    "state": "completed",
                    "progress": 1.0,
                    "confidence": confidence,
                    "last_update": datetime.now(timezone.utc).isoformat()
                }
                
                await self._broadcast_update("sector_completed", {
                    "enterprise": enterprise,
                    "confidence": confidence
                })
                
                await asyncio.sleep(1.0)  # Pause between enterprises
            
            # Cycle completed
            await self._broadcast_update("cycle_completed", {
                "message": "Cosmic Council cycle completed successfully!"
            })
            
        except Exception as e:
            logger.error(f"Error in cycle execution: {e}")
            await self._broadcast_update("cycle_error", {
                "error": str(e)
            })
        
        finally:
            self.visualization_state.cycle_in_progress = False
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the web server"""
        logger.info(f"Starting Cosmic Council Hexagon Web Server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# Sample problems for testing
SAMPLE_PROBLEMS = [
    {
        "title": "AI-Powered Healthcare Transformation",
        "description": "Transform healthcare delivery using AI, machine learning, and telemedicine to improve patient outcomes while reducing costs and increasing accessibility.",
        "complexity": "systemic",
        "domain": "Healthcare & Artificial Intelligence",
        "stakeholders": ["Healthcare Providers", "Patients", "Insurance Companies", "Regulators", "Technology Vendors"],
        "constraints": {"budget": "$25M", "timeline": "3 years", "compliance": "HIPAA, FDA approval required"},
        "success_criteria": ["30% improvement in patient outcomes", "40% cost reduction", "95% regulatory compliance", "80% provider adoption"]
    },
    {
        "title": "Sustainable Smart City Initiative",
        "description": "Develop a comprehensive smart city initiative integrating IoT, AI, and sustainable technologies to improve quality of life and environmental sustainability.",
        "complexity": "complex",
        "domain": "Smart Cities & Technology",
        "stakeholders": ["City Government", "Citizens", "Technology Partners", "Environmental Groups", "Business Community"],
        "constraints": {"budget": "$50M", "timeline": "5 years", "sustainability": "high"},
        "success_criteria": ["Improved quality of life", "Environmental sustainability", "Economic growth", "Digital inclusion"]
    },
    {
        "title": "Digital Transformation Strategy",
        "description": "Develop and implement a comprehensive digital transformation strategy for a mid-size manufacturing company to improve efficiency and competitiveness.",
        "complexity": "moderate",
        "domain": "Digital Transformation & Manufacturing",
        "stakeholders": ["Executive Team", "IT Department", "Operations", "Employees", "Customers"],
        "constraints": {"budget": "$5M", "timeline": "24 months", "disruption": "minimize"},
        "success_criteria": ["30% efficiency improvement", "Digital maturity level 4", "Employee adoption > 80%"]
    }
]

def main():
    """Main function to run the server"""
    server = HexagonWebServer()
    
    print("🌌 Cosmic Council Hexagon Web Server")
    print("=" * 50)
    print("Starting server...")
    print("Open your browser and go to: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")
    print()
    print("Sample problems available:")
    for i, problem in enumerate(SAMPLE_PROBLEMS, 1):
        print(f"  {i}. {problem['title']} ({problem['complexity']})")
    print()
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
