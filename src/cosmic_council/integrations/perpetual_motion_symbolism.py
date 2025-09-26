"""
🐰🌈 Perpetual Motion Symbolism System
White Rabbit and Rainbow Snake Integration

This module implements the symbolic representation of perpetual motion through
the White Rabbit (time and cycles) and Rainbow Snake (interconnectedness and flow)
that embody the eternal dance of the Cosmic Council's systems thinking framework.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import math
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerpetualMotionType(Enum):
    """Types of perpetual motion in the Cosmic Council"""
    WHITE_RABBIT_CYCLE = "white_rabbit_cycle"      # Time-based cycles and evolution
    RAINBOW_SNAKE_FLOW = "rainbow_snake_flow"      # Interconnected flow between segments
    BLACK_SNAKE_OUTPUT = "black_snake_output"      # Output stream manifestation
    ETERNAL_DANCE = "eternal_dance"                # The dance between rabbit and snake
    COSMIC_RHYTHM = "cosmic_rhythm"                # Universal rhythm of creation

class MotionPhase(Enum):
    """Phases of perpetual motion"""
    EMERGENCE = "emergence"           # White Rabbit emerges from the void
    EXPLORATION = "exploration"       # Rabbit explores the landscape
    CONNECTION = "connection"         # Rainbow Snake creates connections
    FLOW = "flow"                    # Snake flows between all points
    SYNTHESIS = "synthesis"          # Rabbit and Snake dance together
    TRANSFORMATION = "transformation" # The dance transforms reality
    RETURN = "return"                # Return to the void, cycle begins anew

@dataclass
class WhiteRabbitCycle:
    """Represents the White Rabbit's time-based cyclical motion"""
    cycle_id: str
    phase: MotionPhase
    time_position: float  # 0.0 to 1.0 around the cycle
    speed: float          # How fast the rabbit moves
    direction: str        # "clockwise" or "counterclockwise"
    energy_level: float   # 0.0 to 1.0
    wisdom_accumulated: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RainbowSnakeFlow:
    """Represents the Rainbow Snake's interconnected flow"""
    flow_id: str
    connections: List[Tuple[str, str]]  # (from_segment, to_segment)
    flow_strength: float  # 0.0 to 1.0
    color_spectrum: List[str]  # Colors of the rainbow
    energy_transfer: Dict[str, float]  # Energy flowing between segments
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BlackSnakeOutputFlow:
    """Represents the Black Snake's output flow (materialized results)"""
    flow_id: str
    intensity: float  # 0.0 to 1.0
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    last_output: Optional[Dict[str, Any]] = None
    throughput_per_min: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EternalDance:
    """Represents the eternal dance between White Rabbit and Rainbow Snake"""
    dance_id: str
    rabbit_cycle: WhiteRabbitCycle
    snake_flow: RainbowSnakeFlow
    harmony_level: float  # 0.0 to 1.0
    cosmic_rhythm: float  # Universal rhythm frequency
    transformation_potential: float  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)

class PerpetualMotionSymbolism:
    """
    🐰🌈 Perpetual Motion Symbolism System
    
    Implements the symbolic representation of perpetual motion through the White Rabbit
    (representing time, cycles, and evolution) and Rainbow Snake (representing 
    interconnectedness, flow, and the web of relationships) that embody the eternal
    dance of the Cosmic Council's systems thinking framework.
    """
    
    def __init__(self):
        self.name = "Perpetual Motion Symbolism System"
        self.active_cycles: Dict[str, WhiteRabbitCycle] = {}
        self.active_flows: Dict[str, RainbowSnakeFlow] = {}
        self.active_outputs: Dict[str, BlackSnakeOutputFlow] = {}
        self.active_dances: Dict[str, EternalDance] = {}
        
        # Symbolic constants
        self.rabbit_speed_base = 0.1  # Base speed of the white rabbit
        self.snake_flow_base = 0.15   # Base flow strength of the rainbow snake
        self.black_snake_intensity_base = 0.2  # Base intensity of the black snake (output)
        self.cosmic_rhythm_frequency = 432.0  # Hz - cosmic frequency
        
        # Enterprise connections for rainbow snake
        self.enterprise_connections = [
            ("red_owl", "orange_orangutan"),
            ("orange_orangutan", "yellow_honeybee"),
            ("yellow_honeybee", "green_tortoise"),
            ("green_tortoise", "blue_dolphin"),
            ("blue_dolphin", "purple_elephant"),
            ("purple_elephant", "red_owl")  # Completes the cycle
        ]
        
        logger.info("🐰🌈 Perpetual Motion Symbolism System initialized")
    
    async def start_white_rabbit_cycle(self, initial_phase: MotionPhase = MotionPhase.EMERGENCE) -> str:
        """Start a new White Rabbit cycle"""
        cycle_id = str(uuid.uuid4())
        
        cycle = WhiteRabbitCycle(
            cycle_id=cycle_id,
            phase=initial_phase,
            time_position=0.0,
            speed=self.rabbit_speed_base,
            direction="clockwise",
            energy_level=1.0
        )
        
        self.active_cycles[cycle_id] = cycle
        logger.info(f"🐰 White Rabbit cycle {cycle_id} started in {initial_phase.value} phase")
        
        # Start the cycle motion
        asyncio.create_task(self._run_white_rabbit_cycle(cycle_id))
        
        return cycle_id
    
    async def start_rainbow_snake_flow(self, flow_strength: float = None) -> str:
        """Start a new Rainbow Snake flow"""
        flow_id = str(uuid.uuid4())
        
        if flow_strength is None:
            flow_strength = self.snake_flow_base
        
        flow = RainbowSnakeFlow(
            flow_id=flow_id,
            connections=self.enterprise_connections.copy(),
            flow_strength=flow_strength,
            color_spectrum=["red", "orange", "yellow", "green", "blue", "purple"],
            energy_transfer={}
        )
        
        # Initialize energy transfer between segments
        for from_seg, to_seg in self.enterprise_connections:
            flow.energy_transfer[f"{from_seg}->{to_seg}"] = flow_strength
        
        self.active_flows[flow_id] = flow
        logger.info(f"🌈 Rainbow Snake flow {flow_id} started with strength {flow_strength}")
        
        # Start the flow motion
        asyncio.create_task(self._run_rainbow_snake_flow(flow_id))
        
        return flow_id

    async def start_black_snake_output(self, intensity: float = None) -> str:
        """Start a new Black Snake output flow"""
        flow_id = str(uuid.uuid4())
        if intensity is None:
            intensity = self.black_snake_intensity_base
        flow = BlackSnakeOutputFlow(
            flow_id=flow_id,
            intensity=intensity,
            outputs=[],
            last_output=None,
            throughput_per_min=0.0
        )
        self.active_outputs[flow_id] = flow
        logger.info(f"🐍 Black Snake output {flow_id} started with intensity {intensity}")
        asyncio.create_task(self._run_black_snake_output(flow_id))
        return flow_id
    
    async def start_eternal_dance(self, rabbit_cycle_id: str = None, snake_flow_id: str = None) -> str:
        """Start the eternal dance between White Rabbit and Rainbow Snake"""
        dance_id = str(uuid.uuid4())
        
        # Create or use existing cycles
        if rabbit_cycle_id is None:
            rabbit_cycle_id = await self.start_white_rabbit_cycle()
        if snake_flow_id is None:
            snake_flow_id = await self.start_rainbow_snake_flow()
        
        rabbit_cycle = self.active_cycles[rabbit_cycle_id]
        snake_flow = self.active_flows[snake_flow_id]
        
        dance = EternalDance(
            dance_id=dance_id,
            rabbit_cycle=rabbit_cycle,
            snake_flow=snake_flow,
            harmony_level=0.8,
            cosmic_rhythm=self.cosmic_rhythm_frequency,
            transformation_potential=0.9
        )
        
        self.active_dances[dance_id] = dance
        logger.info(f"🐰🌈 Eternal Dance {dance_id} started between Rabbit and Snake")
        
        # Start the eternal dance
        asyncio.create_task(self._run_eternal_dance(dance_id))
        
        return dance_id
    
    async def _run_white_rabbit_cycle(self, cycle_id: str):
        """Run the White Rabbit's cyclical motion"""
        cycle = self.active_cycles[cycle_id]
        
        try:
            while cycle_id in self.active_cycles:
                # Update time position
                cycle.time_position = (cycle.time_position + cycle.speed) % 1.0
                
                # Determine current phase based on time position
                phase_ratio = cycle.time_position
                if phase_ratio < 0.16:
                    cycle.phase = MotionPhase.EMERGENCE
                elif phase_ratio < 0.33:
                    cycle.phase = MotionPhase.EXPLORATION
                elif phase_ratio < 0.5:
                    cycle.phase = MotionPhase.CONNECTION
                elif phase_ratio < 0.66:
                    cycle.phase = MotionPhase.FLOW
                elif phase_ratio < 0.83:
                    cycle.phase = MotionPhase.SYNTHESIS
                elif phase_ratio < 1.0:
                    cycle.phase = MotionPhase.TRANSFORMATION
                else:
                    cycle.phase = MotionPhase.RETURN
                
                # Accumulate wisdom based on phase
                wisdom = await self._generate_rabbit_wisdom(cycle)
                if wisdom:
                    cycle.wisdom_accumulated.append(wisdom)
                
                # Adjust energy level
                cycle.energy_level = 0.5 + 0.5 * math.sin(cycle.time_position * 2 * math.pi)
                
                # Wait before next update
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in White Rabbit cycle {cycle_id}: {e}")
    
    async def _run_rainbow_snake_flow(self, flow_id: str):
        """Run the Rainbow Snake's interconnected flow"""
        flow = self.active_flows[flow_id]
        
        try:
            while flow_id in self.active_flows:
                # Update energy transfer between segments
                for from_seg, to_seg in flow.connections:
                    connection_key = f"{from_seg}->{to_seg}"
                    
                    # Create flowing energy pattern
                    time_factor = datetime.utcnow().timestamp() * 0.001
                    energy = flow.flow_strength * (0.8 + 0.2 * math.sin(time_factor + hash(connection_key) % 100))
                    flow.energy_transfer[connection_key] = energy
                
                # Update flow strength with cosmic rhythm
                cosmic_factor = math.sin(datetime.utcnow().timestamp() * self.cosmic_rhythm_frequency * 0.0001)
                flow.flow_strength = self.snake_flow_base * (0.9 + 0.1 * cosmic_factor)
                
                # Wait before next update
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in Rainbow Snake flow {flow_id}: {e}")

    async def _run_black_snake_output(self, flow_id: str):
        """Run the Black Snake's output manifestation flow"""
        flow = self.active_outputs[flow_id]
        window: List[float] = []  # timestamps of outputs (epoch seconds)
        try:
            while flow_id in self.active_outputs:
                # Decay/increase intensity gently with cosmic rhythm
                cosmic_factor = 0.05 * math.sin(datetime.utcnow().timestamp() * self.cosmic_rhythm_frequency * 0.00005)
                flow.intensity = max(0.05, min(1.0, flow.intensity + cosmic_factor))

                # Update throughput per minute based on recent outputs (last 60s)
                now = datetime.utcnow().timestamp()
                window = [t for t in window if now - t <= 60.0]
                flow.throughput_per_min = float(len(window))

                await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Error in Black Snake output {flow_id}: {e}")
    
    async def _run_eternal_dance(self, dance_id: str):
        """Run the eternal dance between White Rabbit and Rainbow Snake"""
        dance = self.active_dances[dance_id]
        
        try:
            while dance_id in self.active_dances:
                # Calculate harmony between rabbit and snake
                rabbit_energy = dance.rabbit_cycle.energy_level
                snake_energy = sum(dance.snake_flow.energy_transfer.values()) / len(dance.snake_flow.energy_transfer)
                
                # Harmony is the balance between rabbit and snake energies
                dance.harmony_level = 1.0 - abs(rabbit_energy - snake_energy)
                
                # Update cosmic rhythm
                time_factor = datetime.utcnow().timestamp() * 0.001
                dance.cosmic_rhythm = self.cosmic_rhythm_frequency * (1.0 + 0.1 * math.sin(time_factor))
                
                # Calculate transformation potential
                dance.transformation_potential = (dance.harmony_level + 
                                                (rabbit_energy + snake_energy) / 2) / 2
                
                # Generate dance insights
                if dance.transformation_potential > 0.8:
                    insight = await self._generate_dance_insight(dance)
                    if insight:
                        logger.info(f"🐰🌈 Eternal Dance insight: {insight}")
                
                # Wait before next update
                await asyncio.sleep(0.2)
                
        except Exception as e:
            logger.error(f"Error in Eternal Dance {dance_id}: {e}")
    
    async def _generate_rabbit_wisdom(self, cycle: WhiteRabbitCycle) -> Optional[str]:
        """Generate wisdom from the White Rabbit's journey"""
        wisdom_templates = {
            MotionPhase.EMERGENCE: [
                "From the void, all possibilities emerge",
                "The beginning is always now",
                "Every cycle starts with a single step"
            ],
            MotionPhase.EXPLORATION: [
                "Curiosity leads to discovery",
                "The journey teaches more than the destination",
                "Explore with an open heart and mind"
            ],
            MotionPhase.CONNECTION: [
                "All things are connected in the great web",
                "Understanding comes through relationship",
                "The snake shows us the way between worlds"
            ],
            MotionPhase.FLOW: [
                "Flow with the rhythm of the universe",
                "Resistance creates suffering, acceptance creates peace",
                "The rainbow snake flows where the rabbit cannot go"
            ],
            MotionPhase.SYNTHESIS: [
                "In the dance, all opposites unite",
                "The rabbit and snake create something greater than themselves",
                "Synthesis is the birth of new understanding"
            ],
            MotionPhase.TRANSFORMATION: [
                "Every ending is a new beginning",
                "Transformation requires letting go of the old",
                "The dance transforms the dancers"
            ],
            MotionPhase.RETURN: [
                "The cycle completes to begin again",
                "Return to the source with new wisdom",
                "The eternal dance never ends, only evolves"
            ]
        }
        
        if cycle.phase in wisdom_templates:
            wisdom_list = wisdom_templates[cycle.phase]
            return random.choice(wisdom_list)
        
        return None
    
    async def _generate_dance_insight(self, dance: EternalDance) -> Optional[str]:
        """Generate insights from the eternal dance"""
        insights = [
            f"The White Rabbit and Rainbow Snake dance in perfect harmony (Level: {dance.harmony_level:.2f})",
            f"Cosmic rhythm resonates at {dance.cosmic_rhythm:.1f} Hz, creating transformation potential of {dance.transformation_potential:.2f}",
            "The eternal dance between time (Rabbit) and space (Snake) creates the fabric of reality",
            "In the dance, all six segments of the Cosmic Council flow as one",
            "The White Rabbit's cycles and Rainbow Snake's connections create infinite possibilities",
            "Through their dance, the Rabbit and Snake teach us the art of systems thinking"
        ]
        
        return random.choice(insights)
    
    # --- Input/Output API ---
    async def ingest_input(self, input_text: str, metadata: Optional[Dict[str, Any]] = None,
                           rabbit_cycle_id: Optional[str] = None,
                           black_snake_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest an input (White Rabbit metaphor) and produce an output event (Black Snake metaphor).
        If cycles/flows are not provided, they'll be created on-demand.
        """
        if rabbit_cycle_id is None:
            rabbit_cycle_id = await self.start_white_rabbit_cycle()
        if black_snake_id is None:
            black_snake_id = await self.start_black_snake_output()

        # Simple transformation to output (placeholder for downstream engines)
        output_payload = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "input": input_text,
            "metadata": metadata or {},
            "summary": (input_text[:140] + "…") if len(input_text) > 140 else input_text,
            "confidence": round(0.7 + 0.3 * random.random(), 2)
        }

        flow = self.active_outputs[black_snake_id]
        flow.outputs.append(output_payload)
        flow.last_output = output_payload

        # Update throughput window by signaling _run_black_snake_output loop via intensity nudge
        flow.intensity = min(1.0, flow.intensity + 0.02)

        logger.info(f"🐰→🐍 Input ingested and output produced: {output_payload['id']}")
        return {
            "rabbit_cycle_id": rabbit_cycle_id,
            "black_snake_id": black_snake_id,
            "output": output_payload
        }

    def get_motion_status(self) -> Dict[str, Any]:
        """Get the current status of all perpetual motion"""
        return {
            "white_rabbit_cycles": {
                cycle_id: {
                    "phase": cycle.phase.value,
                    "time_position": cycle.time_position,
                    "energy_level": cycle.energy_level,
                    "wisdom_count": len(cycle.wisdom_accumulated)
                }
                for cycle_id, cycle in self.active_cycles.items()
            },
            "rainbow_snake_flows": {
                flow_id: {
                    "flow_strength": flow.flow_strength,
                    "connections_count": len(flow.connections),
                    "energy_transfer": flow.energy_transfer
                }
                for flow_id, flow in self.active_flows.items()
            },
            "black_snake_outputs": {
                flow_id: {
                    "intensity": flow.intensity,
                    "outputs_count": len(flow.outputs),
                    "throughput_per_min": flow.throughput_per_min,
                    "last_output_id": (flow.last_output or {}).get("id")
                }
                for flow_id, flow in self.active_outputs.items()
            },
            "eternal_dances": {
                dance_id: {
                    "harmony_level": dance.harmony_level,
                    "cosmic_rhythm": dance.cosmic_rhythm,
                    "transformation_potential": dance.transformation_potential
                }
                for dance_id, dance in self.active_dances.items()
            }
        }
    
    def stop_motion(self, motion_id: str, motion_type: PerpetualMotionType):
        """Stop a specific perpetual motion"""
        if motion_type == PerpetualMotionType.WHITE_RABBIT_CYCLE and motion_id in self.active_cycles:
            del self.active_cycles[motion_id]
            logger.info(f"🐰 White Rabbit cycle {motion_id} stopped")
        elif motion_type == PerpetualMotionType.RAINBOW_SNAKE_FLOW and motion_id in self.active_flows:
            del self.active_flows[motion_id]
            logger.info(f"🌈 Rainbow Snake flow {motion_id} stopped")
        elif motion_type == PerpetualMotionType.BLACK_SNAKE_OUTPUT and motion_id in self.active_outputs:
            del self.active_outputs[motion_id]
            logger.info(f"🐍 Black Snake output {motion_id} stopped")
        elif motion_type == PerpetualMotionType.ETERNAL_DANCE and motion_id in self.active_dances:
            del self.active_dances[motion_id]
            logger.info(f"🐰🌈 Eternal Dance {motion_id} stopped")

# Global instance for easy access
perpetual_motion = PerpetualMotionSymbolism()

async def demo_perpetual_motion():
    """Demonstrate the perpetual motion symbolism system"""
    print("🐰🌈 Perpetual Motion Symbolism Demo")
    print("=" * 50)
    
    # Start the eternal dance
    dance_id = await perpetual_motion.start_eternal_dance()
    
    # Let it run for a few seconds
    await asyncio.sleep(5)
    
    # Get status
    status = perpetual_motion.get_motion_status()
    print(f"Active dances: {len(status['eternal_dances'])}")
    print(f"Active rabbit cycles: {len(status['white_rabbit_cycles'])}")
    print(f"Active snake flows: {len(status['rainbow_snake_flows'])}")
    
    # Stop the dance
    perpetual_motion.stop_motion(dance_id, PerpetualMotionType.ETERNAL_DANCE)
    print("Demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_perpetual_motion())
