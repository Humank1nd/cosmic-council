"""
Model Context Protocols (MCPs) for the Cosmic Council
Each sector at each layer has its own MCP definition for context isolation and recursion efficiency.
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Define LayerType enum for MCP system
class LayerType(Enum):
    """The 12 refinement layers from Deci to Quecto."""
    DECI = "deci"        # 10^-1 - Surface Reasoning
    CENTI = "centi"      # 10^-2 - Problem Decomposition  
    MILLI = "milli"      # 10^-3 - Focused Research
    MICRO = "micro"      # 10^-6 - Detailed Analysis
    NANO = "nano"        # 10^-9 - Symbolic & Formal Methods
    PICO = "pico"        # 10^-12 - Algorithmic Optimization
    FEMTO = "femto"      # 10^-15 - Micro-Mechanistic Modeling
    ATTO = "atto"        # 10^-18 - Edge Case Exploration
    ZEPTO = "zepto"      # 10^-21 - Creative Divergence
    YOCTO = "yocto"      # 10^-24 - Knowledge Compression
    RONTO = "ronto"      # 10^-27 - Meta-Reasoning
    QUECTO = "quecto"    # 10^-30 - Chaos & Breakthroughs


class SectorType(Enum):
    """The six sectors of the Cosmic Council."""
    RED = "red"      # Research & Inquiry
    ORANGE = "orange"  # Planning & Logistics
    YELLOW = "yellow"  # Development & Creativity
    GREEN = "green"    # Budget & Resources
    BLUE = "blue"      # Communication & Marketing
    PURPLE = "purple"  # Reflection & Support


@dataclass
class MCPContext:
    """Runtime context instance for an MCP."""
    context_id: str
    sector: SectorType
    layer: LayerType
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    constraints: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class MCPTransition:
    """Record of context passed between sectors/layers."""
    transition_id: str
    from_sector: SectorType
    to_sector: SectorType
    from_layer: LayerType
    to_layer: LayerType
    context_data: Dict[str, Any]
    transformation_applied: str
    transition_type: str  # 'inter-sector', 'inter-layer', 'recursion'
    created_at: datetime


class MCPDefinition:
    """Model Context Protocol definition for a sector at a specific layer."""
    
    def __init__(self, sector: SectorType, layer: LayerType):
        self.sector = sector
        self.layer = layer
        self.input_schema = self._define_input_schema()
        self.output_schema = self._define_output_schema()
        self.constraints = self._define_constraints()
        self.transformation_rules = self._define_transformation_rules()
    
    def _define_input_schema(self) -> Dict[str, Any]:
        """Define the input schema for this sector/layer combination."""
        base_schemas = {
            SectorType.RED: {
                "problem_statement": {"type": "string", "required": True},
                "hypotheses": {"type": "array", "items": {"type": "string"}},
                "relevant_sources": {"type": "array", "items": {"type": "object"}},
                "knowledge_gaps": {"type": "array", "items": {"type": "string"}}
            },
            SectorType.ORANGE: {
                "research_summary": {"type": "object", "required": True},
                "constraints": {"type": "object", "required": True},
                "dependencies": {"type": "array", "items": {"type": "object"}},
                "timeline": {"type": "object", "required": True}
            },
            SectorType.YELLOW: {
                "plan_doc": {"type": "object", "required": True},
                "design_constraints": {"type": "object", "required": True},
                "prototype_options": {"type": "array", "items": {"type": "object"}},
                "testing_results": {"type": "array", "items": {"type": "object"}}
            },
            SectorType.GREEN: {
                "prototype_summary": {"type": "object", "required": True},
                "resource_request": {"type": "object", "required": True},
                "budget_limits": {"type": "object", "required": True},
                "sustainability_metrics": {"type": "object", "required": True}
            },
            SectorType.BLUE: {
                "approved_solution": {"type": "object", "required": True},
                "audience_profile": {"type": "object", "required": True},
                "message_variants": {"type": "array", "items": {"type": "object"}},
                "risk_assessment": {"type": "object", "required": True}
            },
            SectorType.PURPLE: {
                "final_message": {"type": "object", "required": True},
                "feedback_signals": {"type": "array", "items": {"type": "object"}},
                "user_satisfaction": {"type": "number", "required": True},
                "cycle_outcome": {"type": "string", "required": True}
            }
        }
        
        # Apply layer-specific granularity
        base_schema = base_schemas[self.sector].copy()
        return self._apply_layer_granularity(base_schema)
    
    def _define_output_schema(self) -> Dict[str, Any]:
        """Define the output schema for this sector/layer combination."""
        base_schemas = {
            SectorType.RED: {
                "evidence_blocks": {"type": "array", "items": {"type": "object"}},
                "knowledge_summary": {"type": "object"},
                "research_quality_score": {"type": "number"},
                "gaps_identified": {"type": "array", "items": {"type": "string"}}
            },
            SectorType.ORANGE: {
                "structured_plan": {"type": "object"},
                "milestones": {"type": "array", "items": {"type": "object"}},
                "dependencies_mapped": {"type": "object"},
                "feasibility_score": {"type": "number"}
            },
            SectorType.YELLOW: {
                "prototypes": {"type": "array", "items": {"type": "object"}},
                "assumptions_documented": {"type": "array", "items": {"type": "object"}},
                "testing_results": {"type": "object"},
                "innovation_score": {"type": "number"}
            },
            SectorType.GREEN: {
                "resource_package": {"type": "object"},
                "budget_approval": {"type": "object"},
                "sustainability_report": {"type": "object"},
                "cost_effectiveness_score": {"type": "number"}
            },
            SectorType.BLUE: {
                "communication_packet": {"type": "object"},
                "message_optimized": {"type": "object"},
                "safety_verified": {"type": "boolean"},
                "clarity_score": {"type": "number"}
            },
            SectorType.PURPLE: {
                "reflection_report": {"type": "object"},
                "contradictions_detected": {"type": "array", "items": {"type": "string"}},
                "routing_decision": {"type": "string"},
                "solution_sufficiency_score": {"type": "number"}
            }
        }
        
        base_schema = base_schemas[self.sector].copy()
        return self._apply_layer_granularity(base_schema)
    
    def _define_constraints(self) -> Dict[str, Any]:
        """Define constraints for this sector/layer combination."""
        constraints = {
            "max_context_size": self._get_max_context_size(),
            "processing_time_limit": self._get_processing_time_limit(),
            "quality_thresholds": self._get_quality_thresholds(),
            "resource_limits": self._get_resource_limits()
        }
        return constraints
    
    def _define_transformation_rules(self) -> Dict[str, Any]:
        """Define how to transform context for the next sector/layer."""
        return {
            "context_compression": self._get_compression_rules(),
            "data_filtering": self._get_filtering_rules(),
            "format_conversion": self._get_format_rules(),
            "validation_rules": self._get_validation_rules()
        }
    
    def _apply_layer_granularity(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Apply layer-specific granularity to the schema."""
        layer_granularity = {
            LayerType.DECI: {
                "granularity": "broad",
                "detail_level": "high_level_summaries",
                "context_size": "large",
                "abstraction": "conceptual"
            },
            LayerType.CENTI: {
                "granularity": "structured",
                "detail_level": "organized_components",
                "context_size": "medium",
                "abstraction": "logical"
            },
            LayerType.MILLI: {
                "granularity": "detailed",
                "detail_level": "fine_grained_data",
                "context_size": "medium",
                "abstraction": "operational"
            },
            LayerType.MICRO: {
                "granularity": "precise",
                "detail_level": "quantified_metrics",
                "context_size": "small",
                "abstraction": "analytical"
            },
            LayerType.NANO: {
                "granularity": "atomic",
                "detail_level": "individual_elements",
                "context_size": "small",
                "abstraction": "symbolic"
            },
            LayerType.PICO: {
                "granularity": "optimized",
                "detail_level": "efficiency_focused",
                "context_size": "minimal",
                "abstraction": "algorithmic"
            },
            LayerType.FEMTO: {
                "granularity": "mechanistic",
                "detail_level": "process_components",
                "context_size": "minimal",
                "abstraction": "causal"
            },
            LayerType.ATTO: {
                "granularity": "edge_case",
                "detail_level": "anomaly_focused",
                "context_size": "minimal",
                "abstraction": "stress_test"
            },
            LayerType.ZEPTO: {
                "granularity": "divergent",
                "detail_level": "creative_exploration",
                "context_size": "variable",
                "abstraction": "stochastic"
            },
            LayerType.YOCTO: {
                "granularity": "compressed",
                "detail_level": "pattern_archetypes",
                "context_size": "minimal",
                "abstraction": "meta"
            },
            LayerType.RONTO: {
                "granularity": "meta_reasoning",
                "detail_level": "process_analysis",
                "context_size": "minimal",
                "abstraction": "recursive"
            },
            LayerType.QUECTO: {
                "granularity": "chaos_breakthrough",
                "detail_level": "quantum_inspired",
                "context_size": "minimal",
                "abstraction": "quantum"
            }
        }
        
        granularity = layer_granularity[self.layer]
        
        # Apply granularity modifiers to schema
        if granularity["granularity"] == "broad":
            # Deci: High-level summaries, large context
            for key, value in schema.items():
                if isinstance(value, dict) and "type" in value:
                    if value["type"] == "array":
                        value["max_items"] = 10
                    elif value["type"] == "object":
                        value["max_properties"] = 20
        elif granularity["granularity"] == "atomic":
            # Nano: Individual elements, small context
            for key, value in schema.items():
                if isinstance(value, dict) and "type" in value:
                    if value["type"] == "array":
                        value["max_items"] = 3
                    elif value["type"] == "object":
                        value["max_properties"] = 5
        elif granularity["granularity"] == "minimal":
            # Pico and below: Minimal context
            for key, value in schema.items():
                if isinstance(value, dict) and "type" in value:
                    if value["type"] == "array":
                        value["max_items"] = 1
                    elif value["type"] == "object":
                        value["max_properties"] = 3
        
        schema["_granularity"] = granularity
        return schema
    
    def _get_max_context_size(self) -> int:
        """Get maximum context size for this layer."""
        size_map = {
            LayerType.DECI: 10000,
            LayerType.CENTI: 8000,
            LayerType.MILLI: 6000,
            LayerType.MICRO: 4000,
            LayerType.NANO: 2000,
            LayerType.PICO: 1000,
            LayerType.FEMTO: 500,
            LayerType.ATTO: 250,
            LayerType.ZEPTO: 100,
            LayerType.YOCTO: 50,
            LayerType.RONTO: 25,
            LayerType.QUECTO: 10
        }
        return size_map.get(self.layer, 1000)
    
    def _get_processing_time_limit(self) -> int:
        """Get processing time limit in seconds for this layer."""
        time_map = {
            LayerType.DECI: 300,    # 5 minutes
            LayerType.CENTI: 240,   # 4 minutes
            LayerType.MILLI: 180,   # 3 minutes
            LayerType.MICRO: 120,   # 2 minutes
            LayerType.NANO: 90,     # 1.5 minutes
            LayerType.PICO: 60,     # 1 minute
            LayerType.FEMTO: 45,    # 45 seconds
            LayerType.ATTO: 30,     # 30 seconds
            LayerType.ZEPTO: 20,    # 20 seconds
            LayerType.YOCTO: 15,    # 15 seconds
            LayerType.RONTO: 10,    # 10 seconds
            LayerType.QUECTO: 5     # 5 seconds
        }
        return time_map.get(self.layer, 60)
    
    def _get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality thresholds for this layer."""
        base_thresholds = {
            "min_confidence": 0.5,
            "min_completeness": 0.5,
            "min_accuracy": 0.7
        }
        
        # Adjust thresholds based on layer depth
        if self.layer in [LayerType.DECI, LayerType.CENTI]:
            # Higher layers can be more lenient
            base_thresholds["min_confidence"] = 0.4
            base_thresholds["min_completeness"] = 0.4
        elif self.layer in [LayerType.RONTO, LayerType.QUECTO]:
            # Deepest layers must be very precise
            base_thresholds["min_confidence"] = 0.8
            base_thresholds["min_completeness"] = 0.8
            base_thresholds["min_accuracy"] = 0.9
        
        return base_thresholds
    
    def _get_resource_limits(self) -> Dict[str, Any]:
        """Get resource limits for this layer."""
        return {
            "max_memory_mb": self._get_max_context_size() // 10,
            "max_cpu_seconds": self._get_processing_time_limit(),
            "max_api_calls": 50 if self.layer in [LayerType.DECI, LayerType.CENTI] else 20,
            "max_tokens": self._get_max_context_size() * 2
        }
    
    def _get_compression_rules(self) -> List[str]:
        """Get context compression rules for this layer."""
        if self.layer in [LayerType.DECI, LayerType.CENTI]:
            return ["summarize_key_points", "remove_redundancy", "highlight_critical_info"]
        elif self.layer in [LayerType.MILLI, LayerType.MICRO]:
            return ["compress_data_structures", "optimize_format", "remove_metadata"]
        else:
            return ["minimize_context", "extract_essentials", "atomic_representation"]
    
    def _get_filtering_rules(self) -> List[str]:
        """Get data filtering rules for this layer."""
        return [
            "remove_irrelevant_data",
            "filter_by_relevance_score",
            "maintain_data_integrity",
            "preserve_critical_relationships"
        ]
    
    def _get_format_rules(self) -> List[str]:
        """Get format conversion rules for this layer."""
        return [
            "standardize_data_types",
            "normalize_representations",
            "ensure_compatibility",
            "optimize_for_next_sector"
        ]
    
    def _get_validation_rules(self) -> List[str]:
        """Get validation rules for this layer."""
        return [
            "validate_schema_compliance",
            "check_data_quality",
            "verify_constraints",
            "ensure_completeness"
        ]


class MCPManager:
    """Manages Model Context Protocols for the Cosmic Council."""
    
    def __init__(self):
        self.mcp_definitions = {}
        self.active_contexts = {}
        self.transition_history = []
        self._initialize_mcp_definitions()
    
    def _initialize_mcp_definitions(self):
        """Initialize MCP definitions for all sector/layer combinations."""
        for sector in SectorType:
            for layer in LayerType:
                key = f"{sector.value}_{layer.value}"
                self.mcp_definitions[key] = MCPDefinition(sector, layer)
    
    def get_mcp_definition(self, sector: SectorType, layer: LayerType) -> MCPDefinition:
        """Get MCP definition for a specific sector/layer combination."""
        key = f"{sector.value}_{layer.value}"
        return self.mcp_definitions.get(key)
    
    def create_context(self, sector: SectorType, layer: LayerType, inputs: Dict[str, Any]) -> MCPContext:
        """Create a new MCP context instance."""
        context_id = str(uuid.uuid4())
        mcp_def = self.get_mcp_definition(sector, layer)
        
        # Validate inputs against schema
        self._validate_inputs(inputs, mcp_def.input_schema)
        
        # Apply constraints
        constrained_inputs = self._apply_constraints(inputs, mcp_def.constraints)
        
        context = MCPContext(
            context_id=context_id,
            sector=sector,
            layer=layer,
            inputs=constrained_inputs,
            outputs={},
            constraints=mcp_def.constraints,
            metadata={
                "mcp_version": "1.0",
                "created_by": "mcp_manager",
                "schema_compliant": True
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.active_contexts[context_id] = context
        return context
    
    def update_context_outputs(self, context_id: str, outputs: Dict[str, Any]) -> MCPContext:
        """Update context with outputs from sector processing."""
        if context_id not in self.active_contexts:
            raise ValueError(f"Context {context_id} not found")
        
        context = self.active_contexts[context_id]
        mcp_def = self.get_mcp_definition(context.sector, context.layer)
        
        # Validate outputs against schema
        self._validate_outputs(outputs, mcp_def.output_schema)
        
        # Apply transformation rules
        transformed_outputs = self._apply_transformations(outputs, mcp_def.transformation_rules)
        
        context.outputs = transformed_outputs
        context.updated_at = datetime.utcnow()
        
        return context
    
    def transition_context(self, from_context: MCPContext, to_sector: SectorType, to_layer: LayerType) -> MCPContext:
        """Transition context from one sector/layer to another."""
        mcp_def = self.get_mcp_definition(to_sector, to_layer)
        
        # Transform context for the target sector/layer
        transformed_inputs = self._transform_context_for_target(
            from_context.outputs, 
            from_context.sector, 
            from_context.layer,
            to_sector, 
            to_layer
        )
        
        # Create new context
        new_context = self.create_context(to_sector, to_layer, transformed_inputs)
        
        # Record transition
        # Determine transition type
        if from_context.sector == to_sector and from_context.layer != to_layer:
            transition_type = "layer"
        elif from_context.sector != to_sector:
            transition_type = "sector"
        else:
            transition_type = "recursion"
        
        transition = MCPTransition(
            transition_id=str(uuid.uuid4()),
            from_sector=from_context.sector,
            to_sector=to_sector,
            from_layer=from_context.layer,
            to_layer=to_layer,
            context_data=transformed_inputs,
            transformation_applied=f"from_{from_context.sector.value}_{from_context.layer.value}_to_{to_sector.value}_{to_layer.value}",
            transition_type=transition_type,
            created_at=datetime.utcnow()
        )
        
        self.transition_history.append(transition)
        return new_context
    
    def _validate_inputs(self, inputs: Dict[str, Any], schema: Dict[str, Any]):
        """Validate inputs against MCP schema."""
        for key, value in schema.items():
            if value.get("required", False) and key not in inputs:
                raise ValueError(f"Required input '{key}' missing")
            
            if key in inputs:
                expected_type = value.get("type")
                if expected_type == "array" and not isinstance(inputs[key], list):
                    raise ValueError(f"Input '{key}' must be an array")
                elif expected_type == "object" and not isinstance(inputs[key], dict):
                    raise ValueError(f"Input '{key}' must be an object")
                elif expected_type == "string" and not isinstance(inputs[key], str):
                    raise ValueError(f"Input '{key}' must be a string")
                elif expected_type == "number" and not isinstance(inputs[key], (int, float)):
                    raise ValueError(f"Input '{key}' must be a number")
    
    def _validate_outputs(self, outputs: Dict[str, Any], schema: Dict[str, Any]):
        """Validate outputs against MCP schema."""
        for key, value in schema.items():
            if key in outputs:
                expected_type = value.get("type")
                if expected_type == "array" and not isinstance(outputs[key], list):
                    raise ValueError(f"Output '{key}' must be an array")
                elif expected_type == "object" and not isinstance(outputs[key], dict):
                    raise ValueError(f"Output '{key}' must be an object")
                elif expected_type == "string" and not isinstance(outputs[key], str):
                    raise ValueError(f"Output '{key}' must be a string")
                elif expected_type == "number" and not isinstance(outputs[key], (int, float)):
                    raise ValueError(f"Output '{key}' must be a number")
    
    def _apply_constraints(self, inputs: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Apply MCP constraints to inputs."""
        max_size = constraints.get("max_context_size", 1000)
        
        # Truncate if too large
        inputs_str = json.dumps(inputs)
        if len(inputs_str) > max_size:
            # Apply compression rules
            inputs = self._compress_context(inputs, max_size)
        
        return inputs
    
    def _apply_transformations(self, outputs: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformation rules to outputs."""
        # Apply compression rules
        compression_rules = rules.get("context_compression", [])
        for rule in compression_rules:
            if rule == "summarize_key_points":
                outputs = self._summarize_key_points(outputs)
            elif rule == "remove_redundancy":
                outputs = self._remove_redundancy(outputs)
            elif rule == "minimize_context":
                outputs = self._minimize_context(outputs)
        
        return outputs
    
    def _transform_context_for_target(self, outputs: Dict[str, Any], from_sector: SectorType, from_layer: LayerType, 
                                    to_sector: SectorType, to_layer: LayerType) -> Dict[str, Any]:
        """Transform context for the target sector/layer combination."""
        # Get target MCP definition
        target_mcp = self.get_mcp_definition(to_sector, to_layer)
        
        # Map outputs to target inputs based on sector transition rules
        transformed = {}
        
        # Handle same-sector, different-layer transitions (layer refinement)
        if from_sector == to_sector and from_layer != to_layer:
            # For same sector, preserve core inputs and refine based on layer granularity
            if from_sector == SectorType.RED:
                # Red sector layer refinement
                transformed = {
                    "problem_statement": outputs.get("knowledge_summary", {}).get("original_problem", "Design sustainable housing"),
                    "hypotheses": outputs.get("evidence_blocks", []),
                    "relevant_sources": outputs.get("evidence_blocks", []),
                    "knowledge_gaps": outputs.get("gaps_identified", [])
                }
            elif from_sector == SectorType.ORANGE:
                # Orange sector layer refinement
                transformed = {
                    "research_summary": outputs.get("structured_plan", {}),
                    "constraints": outputs.get("dependencies_mapped", {}),
                    "dependencies": outputs.get("dependencies_mapped", {}).get("dependencies", []),
                    "timeline": outputs.get("structured_plan", {}).get("timeline", {})
                }
            elif from_sector == SectorType.YELLOW:
                # Yellow sector layer refinement
                transformed = {
                    "plan_doc": outputs.get("prototypes", [{}])[0] if outputs.get("prototypes") else {},
                    "design_constraints": outputs.get("design_constraints", {}),
                    "prototype_options": outputs.get("prototypes", []),
                    "testing_results": outputs.get("testing_results", [])
                }
            elif from_sector == SectorType.GREEN:
                # Green sector layer refinement
                transformed = {
                    "prototype_summary": outputs.get("approved_prototypes", [{}])[0] if outputs.get("approved_prototypes") else {},
                    "resource_request": outputs.get("resource_allocations", {}),
                    "budget_limits": outputs.get("budget_constraints", {}),
                    "sustainability_metrics": outputs.get("sustainability_assessment", {})
                }
            elif from_sector == SectorType.BLUE:
                # Blue sector layer refinement
                transformed = {
                    "approved_solution": outputs.get("communication_package", {}),
                    "audience_profile": outputs.get("audience_analysis", {}),
                    "message_variants": outputs.get("message_variants", []),
                    "risk_assessment": outputs.get("risk_analysis", {})
                }
            elif from_sector == SectorType.PURPLE:
                # Purple sector layer refinement
                transformed = {
                    "final_message": outputs.get("reflection_summary", {}),
                    "feedback_signals": outputs.get("feedback_analysis", []),
                    "user_satisfaction": outputs.get("satisfaction_metrics", {}),
                    "cycle_outcome": outputs.get("cycle_assessment", {})
                }
        
        if from_sector == SectorType.RED and to_sector == SectorType.ORANGE:
            # Research → Planning
            transformed = {
                "research_summary": outputs.get("knowledge_summary", {}),
                "constraints": {"time": "flexible", "resources": "standard"},
                "dependencies": outputs.get("evidence_blocks", []),
                "timeline": {"start": "immediate", "end": "flexible"}
            }
        elif from_sector == SectorType.ORANGE and to_sector == SectorType.YELLOW:
            # Planning → Development
            transformed = {
                "plan_doc": outputs.get("structured_plan", {}),
                "design_constraints": outputs.get("dependencies_mapped", {}),
                "prototype_options": [],
                "testing_results": []
            }
        elif from_sector == SectorType.YELLOW and to_sector == SectorType.GREEN:
            # Development → Budget
            transformed = {
                "prototype_summary": outputs.get("prototypes", [{}])[0] if outputs.get("prototypes") else {},
                "resource_request": {"prototypes": outputs.get("prototypes", [])},
                "budget_limits": {"max_cost": 100000},
                "sustainability_metrics": {"carbon_footprint": 0, "resource_usage": {}}
            }
        elif from_sector == SectorType.GREEN and to_sector == SectorType.BLUE:
            # Budget → Communication
            transformed = {
                "approved_solution": outputs.get("resource_package", {}),
                "audience_profile": {"type": "general", "expertise": "mixed"},
                "message_variants": [],
                "risk_assessment": {"level": "low", "factors": []}
            }
        elif from_sector == SectorType.BLUE and to_sector == SectorType.PURPLE:
            # Communication → Reflection
            transformed = {
                "final_message": outputs.get("communication_packet", {}),
                "feedback_signals": [],
                "user_satisfaction": 0.0,
                "cycle_outcome": "pending"
            }
        
        # Apply layer-specific transformations
        if to_layer != from_layer:
            transformed = self._apply_layer_transformation(transformed, from_layer, to_layer)
        
        return transformed
    
    def _apply_layer_transformation(self, context: Dict[str, Any], from_layer: LayerType, to_layer: LayerType) -> Dict[str, Any]:
        """Apply layer-specific transformations when moving between layers."""
        if to_layer.value < from_layer.value:  # Moving to deeper layer
            # Increase granularity
            return self._increase_granularity(context, to_layer)
        else:  # Moving to higher layer
            # Decrease granularity (summarize)
            return self._decrease_granularity(context, to_layer)
    
    def _increase_granularity(self, context: Dict[str, Any], target_layer: LayerType) -> Dict[str, Any]:
        """Increase granularity for deeper layers."""
        if target_layer in [LayerType.MICRO, LayerType.NANO]:
            # Add more detailed metrics
            for key, value in context.items():
                if isinstance(value, dict):
                    value["detailed_metrics"] = {}
                    value["granularity_level"] = target_layer.value
        elif target_layer in [LayerType.PICO, LayerType.FEMTO]:
            # Add optimization parameters
            for key, value in context.items():
                if isinstance(value, dict):
                    value["optimization_params"] = {}
                    value["efficiency_metrics"] = {}
        
        return context
    
    def _decrease_granularity(self, context: Dict[str, Any], target_layer: LayerType) -> Dict[str, Any]:
        """Decrease granularity for higher layers (summarize)."""
        if target_layer in [LayerType.DECI, LayerType.CENTI]:
            # Create high-level summaries
            summarized = {}
            for key, value in context.items():
                if isinstance(value, dict):
                    summarized[key] = {
                        "summary": str(value)[:200] + "..." if len(str(value)) > 200 else str(value),
                        "key_points": list(value.keys())[:5] if isinstance(value, dict) else []
                    }
                else:
                    summarized[key] = value
            return summarized
        
        return context
    
    def _compress_context(self, context: Dict[str, Any], max_size: int) -> Dict[str, Any]:
        """Compress context to fit within size limits."""
        # Simple compression: truncate string values
        compressed = {}
        current_size = 0
        
        for key, value in context.items():
            if isinstance(value, str):
                if current_size + len(value) > max_size:
                    # Truncate
                    remaining = max_size - current_size - 100  # Leave some buffer
                    compressed[key] = value[:remaining] + "..."
                    break
                else:
                    compressed[key] = value
                    current_size += len(value)
            else:
                compressed[key] = value
        
        return compressed
    
    def _summarize_key_points(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize key points in outputs."""
        # Simple summarization
        for key, value in outputs.items():
            if isinstance(value, str) and len(value) > 500:
                outputs[key] = value[:500] + "..."
        return outputs
    
    def _remove_redundancy(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant information from outputs."""
        # Simple redundancy removal
        seen_values = set()
        cleaned = {}
        
        for key, value in outputs.items():
            value_str = str(value)
            if value_str not in seen_values:
                cleaned[key] = value
                seen_values.add(value_str)
        
        return cleaned
    
    def _minimize_context(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Minimize context for deep layers."""
        # Keep only essential information
        essential_keys = ["summary", "score", "decision", "result"]
        minimized = {}
        
        for key, value in outputs.items():
            if any(essential in key.lower() for essential in essential_keys):
                minimized[key] = value
        
        return minimized
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """Get statistics about MCP context usage."""
        return {
            "active_contexts": len(self.active_contexts),
            "total_transitions": len(self.transition_history),
            "mcp_definitions": len(self.mcp_definitions),
            "sectors_covered": len(set(t.from_sector for t in self.transition_history)),
            "layers_used": len(set(t.from_layer for t in self.transition_history))
        }
