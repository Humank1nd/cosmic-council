"""
Cosmic Council Refinement Engine - Layer Definitions
Defines the 12 refinement layers (Deci → Quecto) with their capabilities and toolchains.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json


class LayerType(Enum):
    """Layer types for different problem-solving approaches."""
    LLM = "llm"
    GRAPH_ANALYSIS = "graph_analysis"
    RAG = "rag"
    STATISTICAL = "statistical"
    SYMBOLIC = "symbolic"
    OPTIMIZATION = "optimization"
    SIMULATION = "simulation"
    ADVERSARIAL = "adversarial"
    STOCHASTIC = "stochastic"
    CLUSTERING = "clustering"
    META_LEARNING = "meta_learning"
    QUANTUM_CHAOS = "quantum_chaos"


@dataclass
class LayerCapability:
    """Defines the capabilities and tools available at each layer."""
    name: str
    description: str
    toolchain_type: LayerType
    confidence_threshold: float
    completeness_threshold: float
    max_revolutions: int
    budget_usd: float
    p95_latency_ms: int
    example_reframing: str
    tools: List[str]
    techniques: List[str]


class LayerDefinitions:
    """Defines all 12 refinement layers with their capabilities."""
    
    LAYERS = {
        "deci": LayerCapability(
            name="deci",
            description="Surface Reasoning - Big-picture framing of the problem",
            toolchain_type=LayerType.LLM,
            confidence_threshold=0.80,
            completeness_threshold=0.75,
            max_revolutions=5,
            budget_usd=200.0,
            p95_latency_ms=60000,
            example_reframing="How do we reduce carbon emissions globally?",
            tools=["GPT-5", "Claude", "Gemini", "Natural Language Processing"],
            techniques=["Natural language reasoning", "Stakeholder summaries", "Contextual framing"]
        ),
        
        "centi": LayerCapability(
            name="centi",
            description="Problem Decomposition - Break problem into parts, identify dependencies",
            toolchain_type=LayerType.GRAPH_ANALYSIS,
            confidence_threshold=0.82,
            completeness_threshold=0.78,
            max_revolutions=4,
            budget_usd=150.0,
            p95_latency_ms=45000,
            example_reframing="Which industries account for the largest share?",
            tools=["Neo4j", "NetworkX", "Graph databases", "Logic engines"],
            techniques=["Dependency graphs", "Task trees", "Causal mapping", "System decomposition"]
        ),
        
        "milli": LayerCapability(
            name="milli",
            description="Focused Research - Deep research on each subproblem",
            toolchain_type=LayerType.RAG,
            confidence_threshold=0.84,
            completeness_threshold=0.80,
            max_revolutions=3,
            budget_usd=120.0,
            p95_latency_ms=30000,
            example_reframing="How can steel production be made cleaner?",
            tools=["PostgreSQL", "Weaviate", "Pinecone", "ElasticSearch", "RAG systems"],
            techniques=["Retrieval-augmented generation", "Database queries", "Literature review", "Evidence synthesis"]
        ),
        
        "micro": LayerCapability(
            name="micro",
            description="Detailed Analysis - Precision modeling and validation",
            toolchain_type=LayerType.STATISTICAL,
            confidence_threshold=0.86,
            completeness_threshold=0.82,
            max_revolutions=3,
            budget_usd=100.0,
            p95_latency_ms=25000,
            example_reframing="What innovations in smelting could cut energy?",
            tools=["Pandas", "Scikit-learn", "NumPy", "Simulation frameworks"],
            techniques=["Statistical inference", "Simulation models", "Small-data regression", "Quantified analysis"]
        ),
        
        "nano": LayerCapability(
            name="nano",
            description="Symbolic & Formal Methods - Structured reasoning with rules and logic",
            toolchain_type=LayerType.SYMBOLIC,
            confidence_threshold=0.88,
            completeness_threshold=0.84,
            max_revolutions=3,
            budget_usd=80.0,
            p95_latency_ms=20000,
            example_reframing="What catalysts can reduce CO₂ in steel reactions?",
            tools=["Prolog", "Z3 solver", "Symbolic AI frameworks", "Theorem provers"],
            techniques=["Symbolic logic", "Theorem proving", "Constraint satisfaction", "Formal verification"]
        ),
        
        "pico": LayerCapability(
            name="pico",
            description="Algorithmic Optimization - Find optimal solutions to well-structured problems",
            toolchain_type=LayerType.OPTIMIZATION,
            confidence_threshold=0.90,
            completeness_threshold=0.86,
            max_revolutions=2,
            budget_usd=60.0,
            p95_latency_ms=15000,
            example_reframing="What quantum properties affect catalyst efficiency?",
            tools=["OR-Tools", "Gurobi", "Evolutionary computation", "Heuristic algorithms"],
            techniques=["Linear programming", "Evolutionary algorithms", "Heuristics", "Optimization search"]
        ),
        
        "femto": LayerCapability(
            name="femto",
            description="Micro-Mechanistic Modeling - Simulate inner mechanics of the system",
            toolchain_type=LayerType.SIMULATION,
            confidence_threshold=0.92,
            completeness_threshold=0.88,
            max_revolutions=2,
            budget_usd=50.0,
            p95_latency_ms=12000,
            example_reframing="What resonance effects matter in the reaction?",
            tools=["NetLogo", "Mesa", "Physics engines", "Agent-based modeling"],
            techniques=["Agent-based modeling", "Fine-grained simulation", "Mechanistic modeling", "Emergent behavior analysis"]
        ),
        
        "atto": LayerCapability(
            name="atto",
            description="Edge Case Exploration - Stress-test against rare scenarios and anomalies",
            toolchain_type=LayerType.ADVERSARIAL,
            confidence_threshold=0.94,
            completeness_threshold=0.90,
            max_revolutions=2,
            budget_usd=40.0,
            p95_latency_ms=10000,
            example_reframing="How could quantum algorithms optimize this?",
            tools=["Chaos Monkey", "Fuzz testers", "Adversarial ML", "Stress testing frameworks"],
            techniques=["Adversarial attacks", "Fuzzing", "Chaos engineering", "Edge case analysis"]
        ),
        
        "zepto": LayerCapability(
            name="zepto",
            description="Creative Divergence - Wild exploration of unconventional paths",
            toolchain_type=LayerType.STOCHASTIC,
            confidence_threshold=0.96,
            completeness_threshold=0.92,
            max_revolutions=2,
            budget_usd=30.0,
            p95_latency_ms=8000,
            example_reframing="Exotic particle dynamics",
            tools=["Monte Carlo", "Generative art AI", "Novelty search", "Stochastic optimizers"],
            techniques=["Randomized search", "Stochastic methods", "Divergent thinking", "Creative exploration"]
        ),
        
        "yocto": LayerCapability(
            name="yocto",
            description="Knowledge Compression - Distill patterns from the massive solution space",
            toolchain_type=LayerType.CLUSTERING,
            confidence_threshold=0.98,
            completeness_threshold=0.94,
            max_revolutions=1,
            budget_usd=25.0,
            p95_latency_ms=6000,
            example_reframing="Field interactions",
            tools=["UMAP", "PCA", "Vector DB clustering", "Dimensionality reduction"],
            techniques=["Embedding clustering", "Dimensionality reduction", "Meta-summaries", "Pattern distillation"]
        ),
        
        "ronto": LayerCapability(
            name="ronto",
            description="Meta-Reasoning - Reflect on how the problem-solving process itself is being done",
            toolchain_type=LayerType.META_LEARNING,
            confidence_threshold=0.99,
            completeness_threshold=0.96,
            max_revolutions=1,
            budget_usd=20.0,
            p95_latency_ms=4000,
            example_reframing="Hypothetical constructs",
            tools=["AutoML", "Meta-optimizers", "Reflection agents", "Process mining"],
            techniques=["Meta-learning", "Process mining", "Recursive evaluation", "Methodology refinement"]
        ),
        
        "quecto": LayerCapability(
            name="quecto",
            description="Chaos & Breakthroughs - Last resort chaos-based exploration for breakthrough insights",
            toolchain_type=LayerType.QUANTUM_CHAOS,
            confidence_threshold=1.0,
            completeness_threshold=1.0,
            max_revolutions=1,
            budget_usd=15.0,
            p95_latency_ms=2000,
            example_reframing="Is this even the right framing of reality to solve this?",
            tools=["Quantum annealers", "Stochastic optimizers", "Chaos generators", "Breakthrough algorithms"],
            techniques=["Quantum-inspired search", "High-entropy recombination", "Simulated annealing", "Chaos exploration"]
        )
    }
    
    @classmethod
    def get_layer(cls, layer_name: str) -> Optional[LayerCapability]:
        """Get layer capability by name."""
        return cls.LAYERS.get(layer_name.lower())
    
    @classmethod
    def get_all_layers(cls) -> Dict[str, LayerCapability]:
        """Get all layer definitions."""
        return cls.LAYERS.copy()
    
    @classmethod
    def get_layer_order(cls) -> List[str]:
        """Get layers in order from Deci to Quecto."""
        return [
            "deci", "centi", "milli", "micro", "nano", "pico",
            "femto", "atto", "zepto", "yocto", "ronto", "quecto"
        ]
    
    @classmethod
    def get_next_layer(cls, current_layer: str) -> Optional[str]:
        """Get the next layer in the refinement sequence."""
        order = cls.get_layer_order()
        try:
            current_index = order.index(current_layer.lower())
            if current_index < len(order) - 1:
                return order[current_index + 1]
        except ValueError:
            pass
        return None
    
    @classmethod
    def has_next_layer(cls, current_layer: str) -> bool:
        """Check if there's a next layer available."""
        return cls.get_next_layer(current_layer) is not None
    
    @classmethod
    def get_layer_index(cls, layer_name: str) -> int:
        """Get the index of a layer (0-based)."""
        order = cls.get_layer_order()
        try:
            return order.index(layer_name.lower())
        except ValueError:
            return -1
    
    @classmethod
    def is_valid_layer(cls, layer_name: str) -> bool:
        """Check if a layer name is valid."""
        return layer_name.lower() in cls.LAYERS
    
    @classmethod
    def get_layer_scale_exponent(cls, layer_name: str) -> int:
        """Get the scale exponent for a layer (10^-1, 10^-2, etc.)."""
        order = cls.get_layer_order()
        try:
            index = order.index(layer_name.lower())
            return -(index + 1)  # deci = -1, centi = -2, etc.
        except ValueError:
            return 0
    
    @classmethod
    def get_layers_by_toolchain(cls, toolchain_type: LayerType) -> List[str]:
        """Get all layers that use a specific toolchain type."""
        return [
            name for name, capability in cls.LAYERS.items()
            if capability.toolchain_type == toolchain_type
        ]
    
    @classmethod
    def get_layer_summary(cls, layer_name: str) -> Dict[str, Any]:
        """Get a summary of layer capabilities as a dictionary."""
        layer = cls.get_layer(layer_name)
        if not layer:
            return {}
        
        return {
            "name": layer.name,
            "description": layer.description,
            "toolchain_type": layer.toolchain_type.value,
            "confidence_threshold": layer.confidence_threshold,
            "completeness_threshold": layer.completeness_threshold,
            "max_revolutions": layer.max_revolutions,
            "budget_usd": layer.budget_usd,
            "p95_latency_ms": layer.p95_latency_ms,
            "example_reframing": layer.example_reframing,
            "tools": layer.tools,
            "techniques": layer.techniques,
            "scale_exponent": cls.get_layer_scale_exponent(layer_name),
            "order_index": cls.get_layer_index(layer_name)
        }


class LayerRefinementEngine:
    """Engine for refining questions at different layers."""
    
    @staticmethod
    def refine_question(original_question: str, target_layer: str) -> str:
        """
        Refine a question for a specific layer depth.
        
        Args:
            original_question: The original problem statement
            target_layer: The target layer name (deci, centi, etc.)
            
        Returns:
            Refined question appropriate for the target layer
        """
        layer = LayerDefinitions.get_layer(target_layer)
        if not layer:
            return f"Invalid layer: {target_layer}"
        
        # Get the layer's example reframing pattern
        example = layer.example_reframing
        
        # Simple refinement logic - in practice, this would be more sophisticated
        if target_layer == "deci":
            return f"Broad framing: {original_question}"
        elif target_layer == "centi":
            return f"Subsystem analysis: Which components of '{original_question}' are most critical?"
        elif target_layer == "milli":
            return f"Process focus: How can we improve the processes involved in '{original_question}'?"
        elif target_layer == "micro":
            return f"Component analysis: What specific components affect '{original_question}'?"
        elif target_layer == "nano":
            return f"Material/atomic level: What materials or atomic properties influence '{original_question}'?"
        elif target_layer == "pico":
            return f"Signal interaction: What quantum or signal properties affect '{original_question}'?"
        elif target_layer == "femto":
            return f"Sub-signal resonance: What resonance effects matter in '{original_question}'?"
        elif target_layer == "atto":
            return f"Quantum computation: How could quantum algorithms optimize '{original_question}'?"
        elif target_layer == "zepto":
            return f"Ultra-quantum: What exotic dynamics influence '{original_question}'?"
        elif target_layer == "yocto":
            return f"Sub-energies: What field interactions affect '{original_question}'?"
        elif target_layer == "ronto":
            return f"Exotic frameworks: What hypothetical constructs could solve '{original_question}'?"
        elif target_layer == "quecto":
            return f"Informational substrate: Is '{original_question}' even the right framing of reality?"
        else:
            return f"Refined [{target_layer}] version of: {original_question}"
    
    @staticmethod
    def get_refinement_rationale(from_layer: str, to_layer: str, metrics: Dict[str, Any]) -> str:
        """
        Generate rationale for why a problem is being refined to a deeper layer.
        
        Args:
            from_layer: The current layer
            to_layer: The target layer
            metrics: Performance metrics from the current layer
            
        Returns:
            Rationale text explaining the refinement decision
        """
        confidence = metrics.get('confidence_score', 0.0)
        completeness = metrics.get('completeness_score', 0.0)
        revolutions = metrics.get('revolutions_at_layer', 1)
        
        rationale_parts = [
            f"Refining from {from_layer} to {to_layer} layer due to:"
        ]
        
        if confidence < 0.85:
            rationale_parts.append(f"- Low confidence score ({confidence:.2f} < 0.85)")
        
        if completeness < 0.80:
            rationale_parts.append(f"- Incomplete solution ({completeness:.2f} < 0.80)")
        
        if revolutions >= 3:
            rationale_parts.append(f"- Maximum revolutions reached ({revolutions})")
        
        rationale_parts.append(f"- Need for deeper analysis at {to_layer} scale")
        
        return "\n".join(rationale_parts)


# Example usage and testing
if __name__ == "__main__":
    # Test layer definitions
    print("=== Layer Definitions Test ===")
    
    # Test getting a specific layer
    deci_layer = LayerDefinitions.get_layer("deci")
    print(f"Deci layer: {deci_layer.description}")
    print(f"Tools: {deci_layer.tools}")
    
    # Test layer order
    print(f"\nLayer order: {LayerDefinitions.get_layer_order()}")
    
    # Test next layer
    print(f"Next layer after 'milli': {LayerDefinitions.get_next_layer('milli')}")
    print(f"Has next layer after 'quecto': {LayerDefinitions.has_next_layer('quecto')}")
    
    # Test refinement
    original_question = "How can we reduce global carbon emissions?"
    refined = LayerRefinementEngine.refine_question(original_question, "nano")
    print(f"\nRefined question for nano layer: {refined}")
    
    # Test rationale generation
    metrics = {"confidence_score": 0.75, "completeness_score": 0.70, "revolutions_at_layer": 2}
    rationale = LayerRefinementEngine.get_refinement_rationale("deci", "centi", metrics)
    print(f"\nRefinement rationale:\n{rationale}")
