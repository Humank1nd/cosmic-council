"""
Interactive Hexagon Visualization System for Cosmic Council
Real-time visualization with sector toggling and enterprise integration
"""

import turtle
import math
import time
import asyncio
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json

# Import the Cosmic Council components
from src.core.types import (
    CosmicCouncil, ProblemStatement, ProblemComplexity, 
    EnterpriseType, CycleStatus
)
from working_enhanced_agents import (
    WorkingEnhancedRedOwlAgent, WorkingEnhancedOrangeOrangutanAgent,
    AnalysisDepth
)

class VisualizationMode(Enum):
    """Visualization modes for the hexagon"""
    STATIC = "static"
    INTERACTIVE = "interactive"
    REAL_TIME = "real_time"
    ANIMATED = "animated"

class SectorState(Enum):
    """States for each hexagon sector"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class SectorInfo:
    """Information about a hexagon sector"""
    enterprise: EnterpriseType
    name: str
    animal: str
    color: str
    state: SectorState
    progress: float = 0.0
    confidence: float = 0.0
    last_update: datetime = None
    data: Dict[str, Any] = None

class InteractiveHexagonVisualization:
    """Interactive hexagon visualization system"""
    
    def __init__(self, width: int = 800, height: int = 800):
        self.width = width
        self.height = height
        self.screen = None
        self.turtles = {}
        self.sectors = {}
        self.current_problem = None
        self.council = None
        self.visualization_mode = VisualizationMode.INTERACTIVE
        self.animation_speed = 0.1
        self.update_callbacks = []
        
        # Enterprise configuration
        self.enterprise_config = {
            EnterpriseType.RED_OWL: {
                "name": "Red Owl",
                "animal": "Owl",
                "color": "#FF0000",
                "position": 0  # Top
            },
            EnterpriseType.ORANGE_ORANGUTAN: {
                "name": "Orange Orangutan", 
                "animal": "Orangutan",
                "color": "#FFA500",
                "position": 1  # Top-right
            },
            EnterpriseType.YELLOW_HONEYBEE: {
                "name": "Yellow Honeybee",
                "animal": "Honeybee", 
                "color": "#FFFF00",
                "position": 2  # Bottom-right
            },
            EnterpriseType.GREEN_TORTOISE: {
                "name": "Green Tortoise",
                "animal": "Tortoise",
                "color": "#008000", 
                "position": 3  # Bottom
            },
            EnterpriseType.BLUE_DOLPHIN: {
                "name": "Blue Dolphin",
                "animal": "Dolphin",
                "color": "#0000FF",
                "position": 4  # Bottom-left
            },
            EnterpriseType.PURPLE_ELEPHANT: {
                "name": "Purple Elephant",
                "animal": "Elephant",
                "color": "#4B0082",
                "position": 5  # Top-left
            }
        }
        
        self._initialize_sectors()
    
    def _initialize_sectors(self):
        """Initialize sector information"""
        for enterprise_type, config in self.enterprise_config.items():
            self.sectors[enterprise_type] = SectorInfo(
                enterprise=enterprise_type,
                name=config["name"],
                animal=config["animal"],
                color=config["color"],
                state=SectorState.INACTIVE,
                data={}
            )
    
    def setup_screen(self):
        """Setup the turtle screen"""
        self.screen = turtle.Screen()
        self.screen.setup(width=self.width, height=self.height)
        self.screen.bgcolor("white")
        self.screen.title("Cosmic Council - Interactive Hexagon Visualization")
        self.screen.tracer(0)  # Turn off automatic updates for smooth animation
        
        # Create turtles for each sector
        for enterprise_type in self.enterprise_config.keys():
            t = turtle.Turtle()
            t.speed(0)
            t.hideturtle()
            t.penup()
            self.turtles[enterprise_type] = t
        
        # Create main drawing turtle
        self.main_turtle = turtle.Turtle()
        self.main_turtle.speed(0)
        self.main_turtle.hideturtle()
        self.main_turtle.penup()
        
        # Create text turtle for labels
        self.text_turtle = turtle.Turtle()
        self.text_turtle.speed(0)
        self.text_turtle.hideturtle()
        self.text_turtle.penup()
        
        # Setup keyboard bindings
        self._setup_keyboard_bindings()
    
    def _setup_keyboard_bindings(self):
        """Setup keyboard bindings for interaction"""
        self.screen.listen()
        
        # Enterprise toggles (1-6 keys)
        for i, enterprise_type in enumerate(self.enterprise_config.keys(), 1):
            self.screen.onkeypress(
                lambda et=enterprise_type: self.toggle_sector(et), 
                str(i)
            )
        
        # Special keys
        self.screen.onkeypress(self.start_cycle, "space")
        self.screen.onkeypress(self.reset_visualization, "r")
        self.screen.onkeypress(self.show_help, "h")
        self.screen.onkeypress(self.toggle_animation, "a")
        self.screen.onkeypress(self.cycle_mode, "c")
    
    def draw_hexagon(self, center_x: float = 0, center_y: float = 0, radius: float = 200):
        """Draw the main hexagon structure"""
        self.main_turtle.clear()
        self.main_turtle.penup()
        self.main_turtle.goto(center_x, center_y)
        self.main_turtle.pendown()
        self.main_turtle.pensize(3)
        self.main_turtle.color("black")
        
        # Draw hexagon outline
        for i in range(6):
            angle = math.radians(60 * i)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.main_turtle.goto(x, y)
        
        # Draw center point
        self.main_turtle.penup()
        self.main_turtle.goto(center_x, center_y)
        self.main_turtle.pendown()
        self.main_turtle.dot(10, "black")
        
        # Draw sector dividing lines
        self.main_turtle.penup()
        for i in range(6):
            angle = math.radians(60 * i)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.main_turtle.goto(center_x, center_y)
            self.main_turtle.pendown()
            self.main_turtle.goto(x, y)
            self.main_turtle.penup()
    
    def draw_sector(self, enterprise_type: EnterpriseType, center_x: float = 0, center_y: float = 0, radius: float = 200):
        """Draw a single sector with its current state"""
        sector = self.sectors[enterprise_type]
        position = self.enterprise_config[enterprise_type]["position"]
        
        # Calculate sector vertices
        angle1 = math.radians(60 * position)
        angle2 = math.radians(60 * (position + 1))
        
        x1 = center_x + radius * math.cos(angle1)
        y1 = center_y + radius * math.sin(angle1)
        x2 = center_x + radius * math.cos(angle2)
        y2 = center_y + radius * math.sin(angle2)
        
        # Get turtle for this sector
        t = self.turtles[enterprise_type]
        t.clear()
        
        # Determine sector color based on state
        if sector.state == SectorState.INACTIVE:
            fill_color = "lightgray"
            outline_color = "gray"
        elif sector.state == SectorState.ACTIVE:
            fill_color = sector.color
            outline_color = "black"
        elif sector.state == SectorState.PROCESSING:
            fill_color = sector.color
            outline_color = "orange"
        elif sector.state == SectorState.COMPLETED:
            fill_color = sector.color
            outline_color = "green"
        elif sector.state == SectorState.ERROR:
            fill_color = "red"
            outline_color = "darkred"
        else:
            fill_color = "white"
            outline_color = "black"
        
        # Draw sector
        t.penup()
        t.goto(center_x, center_y)
        t.pendown()
        t.color(outline_color, fill_color)
        t.begin_fill()
        t.goto(x1, y1)
        t.goto(x2, y2)
        t.goto(center_x, center_y)
        t.end_fill()
        
        # Draw progress indicator if processing
        if sector.state == SectorState.PROCESSING and sector.progress > 0:
            self._draw_progress_indicator(t, center_x, center_y, x1, y1, x2, y2, sector.progress)
        
        # Draw confidence indicator
        if sector.confidence > 0:
            self._draw_confidence_indicator(t, center_x, center_y, position, sector.confidence)
    
    def _draw_progress_indicator(self, t: turtle.Turtle, center_x: float, center_y: float, 
                                x1: float, y1: float, x2: float, y2: float, progress: float):
        """Draw progress indicator within sector"""
        # Calculate progress line position
        progress_angle = progress * 60  # 60 degrees per sector
        progress_radius = 150  # Inner radius for progress line
        
        angle1 = math.radians(60 * self.enterprise_config[self.sectors[t].enterprise]["position"])
        progress_x = center_x + progress_radius * math.cos(angle1 + math.radians(progress_angle))
        progress_y = center_y + progress_radius * math.sin(angle1 + math.radians(progress_angle))
        
        t.penup()
        t.goto(center_x, center_y)
        t.pendown()
        t.color("white")
        t.pensize(3)
        t.goto(progress_x, progress_y)
    
    def _draw_confidence_indicator(self, t: turtle.Turtle, center_x: float, center_y: float, 
                                  position: int, confidence: float):
        """Draw confidence indicator as a small circle"""
        # Position confidence indicator near the sector edge
        indicator_radius = 20
        indicator_angle = math.radians(60 * position + 30)  # Middle of sector
        indicator_x = center_x + 120 * math.cos(indicator_angle)
        indicator_y = center_y + 120 * math.sin(indicator_angle)
        
        t.penup()
        t.goto(indicator_x, indicator_y)
        t.pendown()
        
        # Color based on confidence level
        if confidence >= 0.8:
            color = "green"
        elif confidence >= 0.6:
            color = "yellow"
        else:
            color = "red"
        
        t.color(color)
        t.dot(indicator_radius * confidence, color)
    
    def draw_labels(self, center_x: float = 0, center_y: float = 0, radius: float = 200):
        """Draw enterprise labels around the hexagon"""
        self.text_turtle.clear()
        
        for enterprise_type, config in self.enterprise_config.items():
            position = config["position"]
            sector = self.sectors[enterprise_type]
            
            # Calculate label position
            label_radius = radius + 40
            angle = math.radians(60 * position + 30)  # Middle of sector
            x = center_x + label_radius * math.cos(angle)
            y = center_y + label_radius * math.sin(angle)
            
            # Draw enterprise name
            self.text_turtle.penup()
            self.text_turtle.goto(x, y)
            self.text_turtle.pendown()
            self.text_turtle.color("black")
            self.text_turtle.write(
                f"{config['name']}\n({config['animal']})",
                align="center",
                font=("Arial", 10, "bold")
            )
            
            # Draw state indicator
            state_x = x
            state_y = y - 25
            self.text_turtle.penup()
            self.text_turtle.goto(state_x, state_y)
            self.text_turtle.pendown()
            
            state_color = {
                SectorState.INACTIVE: "gray",
                SectorState.ACTIVE: "blue", 
                SectorState.PROCESSING: "orange",
                SectorState.COMPLETED: "green",
                SectorState.ERROR: "red"
            }.get(sector.state, "black")
            
            self.text_turtle.color(state_color)
            self.text_turtle.write(
                f"State: {sector.state.value}",
                align="center",
                font=("Arial", 8, "normal")
            )
            
            # Draw confidence if available
            if sector.confidence > 0:
                conf_x = x
                conf_y = y - 40
                self.text_turtle.penup()
                self.text_turtle.goto(conf_x, conf_y)
                self.text_turtle.pendown()
                self.text_turtle.color("purple")
                self.text_turtle.write(
                    f"Confidence: {sector.confidence:.2f}",
                    align="center",
                    font=("Arial", 8, "normal")
                )
    
    def update_visualization(self):
        """Update the entire visualization"""
        center_x, center_y = 0, 0
        radius = 200
        
        # Draw main hexagon
        self.draw_hexagon(center_x, center_y, radius)
        
        # Draw all sectors
        for enterprise_type in self.enterprise_config.keys():
            self.draw_sector(enterprise_type, center_x, center_y, radius)
        
        # Draw labels
        self.draw_labels(center_x, center_y, radius)
        
        # Update screen
        self.screen.update()
        
        # Call update callbacks
        for callback in self.update_callbacks:
            callback(self.sectors)
    
    def toggle_sector(self, enterprise_type: EnterpriseType):
        """Toggle a sector's active state"""
        sector = self.sectors[enterprise_type]
        if sector.state == SectorState.INACTIVE:
            sector.state = SectorState.ACTIVE
        elif sector.state == SectorState.ACTIVE:
            sector.state = SectorState.INACTIVE
        elif sector.state == SectorState.COMPLETED:
            sector.state = SectorState.ACTIVE  # Allow reactivation
        
        sector.last_update = datetime.now(timezone.utc)
        self.update_visualization()
        print(f"Toggled {sector.name} to {sector.state.value}")
    
    def set_sector_state(self, enterprise_type: EnterpriseType, state: SectorState, 
                        progress: float = 0.0, confidence: float = 0.0, data: Dict[str, Any] = None):
        """Set a sector's state and data"""
        sector = self.sectors[enterprise_type]
        sector.state = state
        sector.progress = progress
        sector.confidence = confidence
        sector.last_update = datetime.now(timezone.utc)
        if data:
            sector.data = data
        
        self.update_visualization()
        print(f"Set {sector.name} to {state.value} (progress: {progress:.2f}, confidence: {confidence:.2f})")
    
    def start_cycle(self):
        """Start a problem-solving cycle"""
        if not self.current_problem:
            print("No problem set. Please set a problem first.")
            return
        
        print("Starting Cosmic Council cycle...")
        
        # Reset all sectors to inactive
        for enterprise_type in self.sectors.keys():
            self.set_sector_state(enterprise_type, SectorState.INACTIVE)
        
        # Start the cycle in a separate thread
        cycle_thread = threading.Thread(target=self._run_cycle_async)
        cycle_thread.daemon = True
        cycle_thread.start()
    
    def _run_cycle_async(self):
        """Run the cycle asynchronously"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._execute_cycle())
        loop.close()
    
    async def _execute_cycle(self):
        """Execute the problem-solving cycle"""
        if not self.council:
            self.council = CosmicCouncil()
        
        # Process through each enterprise in order
        processing_order = [
            EnterpriseType.RED_OWL,
            EnterpriseType.ORANGE_ORANGUTAN,
            EnterpriseType.YELLOW_HONEYBEE,
            EnterpriseType.GREEN_TORTOISE,
            EnterpriseType.BLUE_DOLPHIN,
            EnterpriseType.PURPLE_ELEPHANT
        ]
        
        for i, enterprise_type in enumerate(processing_order):
            # Set sector to processing
            self.set_sector_state(enterprise_type, SectorState.PROCESSING, progress=0.0)
            
            # Simulate processing with progress updates
            for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
                await asyncio.sleep(0.5)  # Simulate processing time
                self.set_sector_state(enterprise_type, SectorState.PROCESSING, progress=progress)
            
            # Simulate completion with confidence score
            confidence = 0.7 + (i * 0.05)  # Increasing confidence
            self.set_sector_state(enterprise_type, SectorState.COMPLETED, 
                                progress=1.0, confidence=confidence)
            
            await asyncio.sleep(1.0)  # Pause between enterprises
        
        print("Cosmic Council cycle completed!")
    
    def set_problem(self, problem: ProblemStatement):
        """Set the current problem for the visualization"""
        self.current_problem = problem
        print(f"Problem set: {problem.title}")
        print(f"Complexity: {problem.complexity.value}")
        print(f"Stakeholders: {len(problem.stakeholders)}")
    
    def reset_visualization(self):
        """Reset the visualization to initial state"""
        for enterprise_type in self.sectors.keys():
            self.set_sector_state(enterprise_type, SectorState.INACTIVE, 
                                progress=0.0, confidence=0.0)
        print("Visualization reset")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Cosmic Council Hexagon Visualization Controls:

Number Keys (1-6): Toggle enterprise sectors
  - 1: Red Owl (Research)
  - 2: Orange Orangutan (Planning)  
  - 3: Yellow Honeybee (Development)
  - 4: Green Tortoise (Resources)
  - 5: Blue Dolphin (Communication)
  - 6: Purple Elephant (Support)

Special Keys:
  - Space: Start problem-solving cycle
  - R: Reset visualization
  - H: Show this help
  - A: Toggle animation mode
  - C: Cycle through visualization modes

Sector States:
  - Gray: Inactive
  - Colored: Active
  - Orange outline: Processing
  - Green outline: Completed
  - Red: Error

Confidence Indicators:
  - Green dot: High confidence (>0.8)
  - Yellow dot: Medium confidence (0.6-0.8)
  - Red dot: Low confidence (<0.6)
        """
        print(help_text)
    
    def toggle_animation(self):
        """Toggle animation mode"""
        if self.visualization_mode == VisualizationMode.STATIC:
            self.visualization_mode = VisualizationMode.ANIMATED
            self.screen.tracer(1, 10)  # Enable animation
        else:
            self.visualization_mode = VisualizationMode.STATIC
            self.screen.tracer(0)  # Disable animation
        print(f"Animation mode: {self.visualization_mode.value}")
    
    def cycle_mode(self):
        """Cycle through visualization modes"""
        modes = list(VisualizationMode)
        current_index = modes.index(self.visualization_mode)
        next_index = (current_index + 1) % len(modes)
        self.visualization_mode = modes[next_index]
        print(f"Visualization mode: {self.visualization_mode.value}")
    
    def add_update_callback(self, callback: Callable):
        """Add a callback function to be called on visualization updates"""
        self.update_callbacks.append(callback)
    
    def run(self):
        """Run the interactive visualization"""
        self.setup_screen()
        self.update_visualization()
        self.show_help()
        
        print("Interactive Hexagon Visualization started!")
        print("Press 'h' for help, 'q' to quit")
        
        try:
            turtle.done()
        except turtle.Terminator:
            print("Visualization closed")

# Demo function
def demo_interactive_hexagon():
    """Demonstrate the interactive hexagon visualization"""
    print("Cosmic Council Interactive Hexagon Visualization Demo")
    print("=" * 60)
    
    # Create visualization
    viz = InteractiveHexagonVisualization()
    
    # Create a sample problem
    problem = ProblemStatement(
        title="Smart City Development",
        description="Develop a comprehensive smart city initiative integrating IoT, AI, and sustainable technologies.",
        complexity=ProblemComplexity.COMPLEX,
        domain="Smart Cities & Technology",
        stakeholders=["City Government", "Citizens", "Technology Partners", "Environmental Groups"],
        constraints={"budget": "$50M", "timeline": "5 years"},
        success_criteria=["Improved quality of life", "Environmental sustainability", "Economic growth"]
    )
    
    # Set the problem
    viz.set_problem(problem)
    
    # Add update callback for logging
    def log_update(sectors):
        active_sectors = [s.name for s in sectors.values() if s.state == SectorState.ACTIVE]
        if active_sectors:
            print(f"Active sectors: {', '.join(active_sectors)}")
    
    viz.add_update_callback(log_update)
    
    # Run the visualization
    viz.run()

if __name__ == "__main__":
    demo_interactive_hexagon()
