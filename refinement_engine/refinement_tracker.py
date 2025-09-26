"""
Cosmic Council Refinement Engine - Refinement Tracking and Genealogy Logging
Tracks the complete genealogy of problem refinements and provides audit trails.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
import json
import logging
from datetime import datetime
import uuid
from enum import Enum

try:
    from .layers import LayerDefinitions
    from .escalator import EscalatorDecision, EscalatorAction
except ImportError:
    # For testing
    from layers import LayerDefinitions
    from escalator import EscalatorDecision, EscalatorAction


class TrackingEventType(Enum):
    """Types of events that can be tracked."""
    PROBLEM_CREATED = "problem_created"
    LAYER_RUN_STARTED = "layer_run_started"
    LAYER_RUN_COMPLETED = "layer_run_completed"
    LAYER_RUN_FAILED = "layer_run_failed"
    SECTOR_EXECUTED = "sector_executed"
    REFINEMENT_DECISION = "refinement_decision"
    ESCALATOR_DECISION = "escalator_decision"
    PROBLEM_RESOLVED = "problem_resolved"
    ANSWER_CREATED = "answer_created"


@dataclass
class TrackingEvent:
    """Represents a tracking event in the refinement process."""
    event_id: str
    event_type: TrackingEventType
    problem_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RefinementNode:
    """Represents a node in the refinement genealogy tree."""
    node_id: str
    problem_id: str
    layer: str
    revolution: int
    parent_node_id: Optional[str] = None
    children_node_ids: List[str] = field(default_factory=list)
    layer_run_id: Optional[str] = None
    status: str = "pending"
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class RefinementPath:
    """Represents a complete path through the refinement tree."""
    path_id: str
    problem_id: str
    nodes: List[RefinementNode]
    total_cost: float = 0.0
    total_latency: int = 0
    final_confidence: float = 0.0
    final_completeness: float = 0.0
    path_quality_score: float = 0.0


class RefinementTracker:
    """
    Tracks the complete genealogy of problem refinements.
    
    This class provides:
    1. Event tracking and audit trails
    2. Refinement genealogy trees
    3. Path analysis and optimization
    4. Performance metrics and insights
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.events: List[TrackingEvent] = []
        self.refinement_nodes: Dict[str, RefinementNode] = {}
        self.problem_genealogies: Dict[str, List[RefinementNode]] = {}
        self.refinement_paths: Dict[str, List[RefinementPath]] = {}
    
    def track_event(
        self,
        event_type: TrackingEventType,
        problem_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track an event in the refinement process.
        
        Args:
            event_type: Type of event to track
            problem_id: ID of the problem
            data: Event data
            metadata: Additional metadata
            
        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())
        
        event = TrackingEvent(
            event_id=event_id,
            event_type=event_type,
            problem_id=problem_id,
            timestamp=datetime.utcnow(),
            data=data,
            metadata=metadata or {}
        )
        
        self.events.append(event)
        
        self.logger.debug(f"Tracked event {event_type.value} for problem {problem_id}")
        
        return event_id
    
    def create_refinement_node(
        self,
        problem_id: str,
        layer: str,
        revolution: int,
        parent_node_id: Optional[str] = None,
        layer_run_id: Optional[str] = None
    ) -> str:
        """
        Create a new refinement node.
        
        Args:
            problem_id: ID of the problem
            layer: Layer name
            revolution: Revolution number at this layer
            parent_node_id: ID of parent node (for refinements)
            layer_run_id: Associated layer run ID
            
        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())
        
        node = RefinementNode(
            node_id=node_id,
            problem_id=problem_id,
            layer=layer,
            revolution=revolution,
            parent_node_id=parent_node_id,
            layer_run_id=layer_run_id
        )
        
        self.refinement_nodes[node_id] = node
        
        # Add to problem genealogy
        if problem_id not in self.problem_genealogies:
            self.problem_genealogies[problem_id] = []
        self.problem_genealogies[problem_id].append(node)
        
        # Update parent node if exists
        if parent_node_id and parent_node_id in self.refinement_nodes:
            self.refinement_nodes[parent_node_id].children_node_ids.append(node_id)
        
        # Track the event
        self.track_event(
            TrackingEventType.LAYER_RUN_STARTED,
            problem_id,
            {
                "node_id": node_id,
                "layer": layer,
                "revolution": revolution,
                "parent_node_id": parent_node_id
            }
        )
        
        self.logger.info(f"Created refinement node {node_id} for problem {problem_id} at {layer} layer (revolution {revolution})")
        
        return node_id
    
    def update_refinement_node(
        self,
        node_id: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        completed_at: Optional[datetime] = None
    ):
        """
        Update a refinement node with completion data.
        
        Args:
            node_id: ID of the node to update
            status: New status
            metrics: Performance metrics
            completed_at: Completion timestamp
        """
        if node_id not in self.refinement_nodes:
            raise ValueError(f"Refinement node {node_id} not found")
        
        node = self.refinement_nodes[node_id]
        node.status = status
        node.completed_at = completed_at or datetime.utcnow()
        
        if metrics:
            node.metrics.update(metrics)
        
        # Track the event
        self.track_event(
            TrackingEventType.LAYER_RUN_COMPLETED if status == "completed" else TrackingEventType.LAYER_RUN_FAILED,
            node.problem_id,
            {
                "node_id": node_id,
                "layer": node.layer,
                "revolution": node.revolution,
                "status": status,
                "metrics": metrics or {}
            }
        )
        
        self.logger.info(f"Updated refinement node {node_id} with status {status}")
    
    def track_escalator_decision(
        self,
        problem_id: str,
        decision: EscalatorDecision,
        current_node_id: str
    ) -> str:
        """
        Track an escalator decision.
        
        Args:
            problem_id: ID of the problem
            decision: The escalator decision
            current_node_id: Current refinement node ID
            
        Returns:
            Event ID
        """
        return self.track_event(
            TrackingEventType.ESCALATOR_DECISION,
            problem_id,
            {
                "action": decision.action.value,
                "reason": decision.reason,
                "from_layer": decision.from_layer,
                "to_layer": decision.to_layer,
                "refined_question": decision.refined_question,
                "current_node_id": current_node_id,
                "metrics": decision.metrics
            }
        )
    
    def track_refinement(
        self,
        problem_id: str,
        from_layer: str,
        to_layer: str,
        rationale: str,
        refined_question: str,
        parent_node_id: str
    ) -> str:
        """
        Track a refinement decision.
        
        Args:
            problem_id: ID of the problem
            from_layer: Source layer
            to_layer: Target layer
            rationale: Refinement rationale
            refined_question: Refined question
            parent_node_id: Parent node ID
            
        Returns:
            Event ID
        """
        return self.track_event(
            TrackingEventType.REFINEMENT_DECISION,
            problem_id,
            {
                "from_layer": from_layer,
                "to_layer": to_layer,
                "rationale": rationale,
                "refined_question": refined_question,
                "parent_node_id": parent_node_id
            }
        )
    
    def track_answer_creation(
        self,
        problem_id: str,
        answer_data: Dict[str, Any],
        node_id: str
    ) -> str:
        """
        Track the creation of an answer.
        
        Args:
            problem_id: ID of the problem
            answer_data: Answer data
            node_id: Associated node ID
            
        Returns:
            Event ID
        """
        return self.track_event(
            TrackingEventType.ANSWER_CREATED,
            problem_id,
            {
                "answer_data": answer_data,
                "node_id": node_id
            }
        )
    
    def get_problem_genealogy(self, problem_id: str) -> Dict[str, Any]:
        """
        Get the complete genealogy of a problem.
        
        Args:
            problem_id: ID of the problem
            
        Returns:
            Genealogy data
        """
        if problem_id not in self.problem_genealogies:
            return {"error": "Problem not found"}
        
        nodes = self.problem_genealogies[problem_id]
        
        # Build genealogy tree
        genealogy = {
            "problem_id": problem_id,
            "total_nodes": len(nodes),
            "layers_visited": list(set(node.layer for node in nodes)),
            "max_depth": self._calculate_max_depth(nodes),
            "total_revolutions": sum(node.revolution for node in nodes),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "layer": node.layer,
                    "revolution": node.revolution,
                    "parent_node_id": node.parent_node_id,
                    "children_count": len(node.children_node_ids),
                    "status": node.status,
                    "created_at": node.created_at.isoformat(),
                    "completed_at": node.completed_at.isoformat() if node.completed_at else None,
                    "metrics": node.metrics
                }
                for node in nodes
            ],
            "refinement_paths": self._get_refinement_paths(problem_id)
        }
        
        return genealogy
    
    def _calculate_max_depth(self, nodes: List[RefinementNode]) -> int:
        """Calculate the maximum depth of the refinement tree."""
        if not nodes:
            return 0
        
        # Find root nodes (no parent)
        root_nodes = [node for node in nodes if node.parent_node_id is None]
        
        max_depth = 0
        for root in root_nodes:
            depth = self._calculate_node_depth(root, nodes)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_node_depth(self, node: RefinementNode, all_nodes: List[RefinementNode]) -> int:
        """Calculate the depth of a specific node."""
        if not node.children_node_ids:
            return 1
        
        max_child_depth = 0
        for child_id in node.children_node_ids:
            child_node = next((n for n in all_nodes if n.node_id == child_id), None)
            if child_node:
                child_depth = self._calculate_node_depth(child_node, all_nodes)
                max_child_depth = max(max_child_depth, child_depth)
        
        return 1 + max_child_depth
    
    def _get_refinement_paths(self, problem_id: str) -> List[Dict[str, Any]]:
        """Get all refinement paths for a problem."""
        if problem_id not in self.problem_genealogies:
            return []
        
        nodes = self.problem_genealogies[problem_id]
        
        # Find all leaf nodes (nodes with no children)
        leaf_nodes = [node for node in nodes if not node.children_node_ids]
        
        paths = []
        for leaf in leaf_nodes:
            path = self._build_path_to_root(leaf, nodes)
            if path:
                paths.append({
                    "path_id": str(uuid.uuid4()),
                    "nodes": [
                        {
                            "node_id": node.node_id,
                            "layer": node.layer,
                            "revolution": node.revolution,
                            "status": node.status,
                            "metrics": node.metrics
                        }
                        for node in path
                    ],
                    "total_cost": sum(node.metrics.get("total_cost_usd", 0.0) for node in path),
                    "total_latency": sum(node.metrics.get("total_latency_ms", 0) for node in path),
                    "final_confidence": path[-1].metrics.get("confidence_score", 0.0) if path else 0.0,
                    "final_completeness": path[-1].metrics.get("completeness_score", 0.0) if path else 0.0
                })
        
        return paths
    
    def _build_path_to_root(self, node: RefinementNode, all_nodes: List[RefinementNode]) -> List[RefinementNode]:
        """Build a path from a node to the root."""
        path = [node]
        current = node
        
        while current.parent_node_id:
            parent = next((n for n in all_nodes if n.node_id == current.parent_node_id), None)
            if parent:
                path.append(parent)
                current = parent
            else:
                break
        
        return list(reversed(path))  # Return path from root to leaf
    
    def get_refinement_analytics(self, problem_id: str) -> Dict[str, Any]:
        """
        Get analytics for a problem's refinement process.
        
        Args:
            problem_id: ID of the problem
            
        Returns:
            Analytics data
        """
        if problem_id not in self.problem_genealogies:
            return {"error": "Problem not found"}
        
        nodes = self.problem_genealogies[problem_id]
        events = [e for e in self.events if e.problem_id == problem_id]
        
        # Calculate analytics
        analytics = {
            "problem_id": problem_id,
            "total_processing_time": self._calculate_total_processing_time(nodes),
            "total_cost": sum(node.metrics.get("total_cost_usd", 0.0) for node in nodes),
            "total_latency": sum(node.metrics.get("total_latency_ms", 0) for node in nodes),
            "layers_visited": list(set(node.layer for node in nodes)),
            "revolutions_per_layer": self._calculate_revolutions_per_layer(nodes),
            "success_rate": self._calculate_success_rate(nodes),
            "refinement_efficiency": self._calculate_refinement_efficiency(nodes),
            "event_timeline": [
                {
                    "event_type": event.event_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data
                }
                for event in sorted(events, key=lambda e: e.timestamp)
            ],
            "performance_trends": self._calculate_performance_trends(nodes)
        }
        
        return analytics
    
    def _calculate_total_processing_time(self, nodes: List[RefinementNode]) -> int:
        """Calculate total processing time in milliseconds."""
        if not nodes:
            return 0
        
        start_time = min(node.created_at for node in nodes)
        end_time = max(node.completed_at for node in nodes if node.completed_at)
        
        if end_time:
            return int((end_time - start_time).total_seconds() * 1000)
        return 0
    
    def _calculate_revolutions_per_layer(self, nodes: List[RefinementNode]) -> Dict[str, int]:
        """Calculate revolutions per layer."""
        revolutions = {}
        for node in nodes:
            if node.layer not in revolutions:
                revolutions[node.layer] = 0
            revolutions[node.layer] = max(revolutions[node.layer], node.revolution)
        return revolutions
    
    def _calculate_success_rate(self, nodes: List[RefinementNode]) -> float:
        """Calculate success rate of layer runs."""
        if not nodes:
            return 0.0
        
        completed_nodes = [node for node in nodes if node.status == "completed"]
        return len(completed_nodes) / len(nodes)
    
    def _calculate_refinement_efficiency(self, nodes: List[RefinementNode]) -> float:
        """Calculate refinement efficiency score."""
        if not nodes:
            return 0.0
        
        # Calculate efficiency based on confidence and completeness improvements
        confidence_scores = [node.metrics.get("confidence_score", 0.0) for node in nodes if node.metrics]
        completeness_scores = [node.metrics.get("completeness_score", 0.0) for node in nodes if node.metrics]
        
        if not confidence_scores or not completeness_scores:
            return 0.0
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        avg_completeness = sum(completeness_scores) / len(completeness_scores)
        
        # Efficiency is the average of confidence and completeness
        return (avg_confidence + avg_completeness) / 2.0
    
    def _calculate_performance_trends(self, nodes: List[RefinementNode]) -> Dict[str, List[float]]:
        """Calculate performance trends over time."""
        # Sort nodes by creation time
        sorted_nodes = sorted(nodes, key=lambda n: n.created_at)
        
        trends = {
            "confidence": [],
            "completeness": [],
            "cost": [],
            "latency": []
        }
        
        for node in sorted_nodes:
            if node.metrics:
                trends["confidence"].append(node.metrics.get("confidence_score", 0.0))
                trends["completeness"].append(node.metrics.get("completeness_score", 0.0))
                trends["cost"].append(node.metrics.get("total_cost_usd", 0.0))
                trends["latency"].append(node.metrics.get("total_latency_ms", 0))
        
        return trends
    
    def get_audit_trail(self, problem_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete audit trail for a problem.
        
        Args:
            problem_id: ID of the problem
            
        Returns:
            List of audit trail events
        """
        events = [e for e in self.events if e.problem_id == problem_id]
        
        return [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "metadata": event.metadata
            }
            for event in sorted(events, key=lambda e: e.timestamp)
        ]
    
    def export_genealogy_data(self, problem_id: str) -> Dict[str, Any]:
        """
        Export complete genealogy data for a problem.
        
        Args:
            problem_id: ID of the problem
            
        Returns:
            Complete genealogy data
        """
        return {
            "genealogy": self.get_problem_genealogy(problem_id),
            "analytics": self.get_refinement_analytics(problem_id),
            "audit_trail": self.get_audit_trail(problem_id)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test refinement tracker
    print("=== Refinement Tracker Test ===")
    
    tracker = RefinementTracker()
    
    # Simulate a problem refinement process
    problem_id = "test-problem-001"
    
    # Create initial node
    node1 = tracker.create_refinement_node(problem_id, "deci", 1)
    
    # Update node with completion
    tracker.update_refinement_node(node1, "completed", {
        "confidence_score": 0.75,
        "completeness_score": 0.70,
        "total_cost_usd": 50.0,
        "total_latency_ms": 30000
    })
    
    # Track refinement decision
    tracker.track_refinement(problem_id, "deci", "centi", "Low confidence", "Refined question", node1)
    
    # Create refined node
    node2 = tracker.create_refinement_node(problem_id, "centi", 1, parent_node_id=node1)
    
    # Update refined node
    tracker.update_refinement_node(node2, "completed", {
        "confidence_score": 0.85,
        "completeness_score": 0.80,
        "total_cost_usd": 75.0,
        "total_latency_ms": 45000
    })
    
    # Track answer creation
    tracker.track_answer_creation(problem_id, {"solution": "Test solution"}, node2)
    
    # Get genealogy
    genealogy = tracker.get_problem_genealogy(problem_id)
    print(f"Genealogy: {len(genealogy['nodes'])} nodes, {len(genealogy['layers_visited'])} layers")
    
    # Get analytics
    analytics = tracker.get_refinement_analytics(problem_id)
    print(f"Analytics: {analytics['total_cost']:.2f} cost, {analytics['success_rate']:.2f} success rate")
    
    # Get audit trail
    audit_trail = tracker.get_audit_trail(problem_id)
    print(f"Audit trail: {len(audit_trail)} events")
