"""
ORANGE ORANGUTAN - Dependency Resolver.

Resolves dependencies between actions and produces a valid execution order.
This implements Criterion 1: Actions are topologically sorted by dependencies.

The resolver:
- Infers implicit dependencies from action categories
- Validates explicit dependencies
- Produces a topologically sorted execution order
- Detects cycles and handles them gracefully
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import structlog

from .models import (
    ActionCategory,
    ActionStep,
    ActionPlan,
    Dependency,
)

logger = structlog.get_logger(__name__)


@dataclass
class DependencyResolutionResult:
    """Result of resolving dependencies."""
    execution_order: List[str] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    cycles_detected: List[List[str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    valid: bool = True
    duration_ms: int = 0


# Implicit dependency rules: category A should come before category B
CATEGORY_ORDERING: List[Tuple[ActionCategory, ActionCategory]] = [
    # Investigation before action
    (ActionCategory.INVESTIGATION, ActionCategory.CONFIGURATION),
    (ActionCategory.INVESTIGATION, ActionCategory.DEPLOYMENT),
    (ActionCategory.INVESTIGATION, ActionCategory.DATABASE),
    (ActionCategory.INVESTIGATION, ActionCategory.NETWORK),
    (ActionCategory.INVESTIGATION, ActionCategory.SECURITY),
    (ActionCategory.INVESTIGATION, ActionCategory.SCALING),
    (ActionCategory.INVESTIGATION, ActionCategory.RESTART),

    # Configuration before deployment
    (ActionCategory.CONFIGURATION, ActionCategory.DEPLOYMENT),

    # Restart after configuration/deployment
    (ActionCategory.CONFIGURATION, ActionCategory.RESTART),
    (ActionCategory.DEPLOYMENT, ActionCategory.RESTART),

    # Monitoring after actions
    (ActionCategory.DEPLOYMENT, ActionCategory.MONITORING),
    (ActionCategory.RESTART, ActionCategory.MONITORING),
    (ActionCategory.CONFIGURATION, ActionCategory.MONITORING),
    (ActionCategory.SCALING, ActionCategory.MONITORING),

    # Communication typically last
    (ActionCategory.MONITORING, ActionCategory.COMMUNICATION),
]


class DependencyResolver:
    """
    Resolves action dependencies and produces execution order.

    This is critical for Criterion 1: Dependency ordering.
    Actions must be executed in the correct order.
    """

    def __init__(
        self,
        infer_implicit_dependencies: bool = True,
    ):
        """
        Initialize the dependency resolver.

        Args:
            infer_implicit_dependencies: Whether to infer deps from categories
        """
        self.infer_implicit = infer_implicit_dependencies
        logger.info(
            "dependency_resolver_initialized",
            infer_implicit=infer_implicit_dependencies,
        )

    def resolve(
        self,
        actions: List[ActionStep],
        explicit_dependencies: Optional[List[Dependency]] = None,
    ) -> DependencyResolutionResult:
        """
        Resolve dependencies and produce execution order.

        Args:
            actions: List of actions to order
            explicit_dependencies: Explicit dependencies between actions

        Returns:
            DependencyResolutionResult with valid execution order
        """
        start_time = time.time()
        explicit_dependencies = explicit_dependencies or []

        if not actions:
            return DependencyResolutionResult(duration_ms=0)

        # Build action lookup
        action_map = {a.id: a for a in actions}

        # Collect all dependencies
        all_deps: List[Dependency] = list(explicit_dependencies)
        warnings: List[str] = []

        # Add dependencies from action.depends_on
        for action in actions:
            for dep_id in action.depends_on:
                if dep_id not in action_map:
                    warnings.append(f"Action {action.id} depends on unknown action {dep_id}")
                    continue
                all_deps.append(Dependency(
                    from_action_id=dep_id,
                    to_action_id=action.id,
                    dependency_type="requires",
                    reason="Explicit dependency",
                ))

        # Infer implicit dependencies from categories
        if self.infer_implicit:
            inferred = self._infer_dependencies(actions, action_map)
            all_deps.extend(inferred)

        # Build dependency graph
        graph, in_degree = self._build_graph(actions, all_deps)

        # Topological sort using Kahn's algorithm
        execution_order, cycles = self._topological_sort(
            actions, graph, in_degree, action_map
        )

        # Handle cycles
        if cycles:
            warnings.append(f"Detected {len(cycles)} dependency cycles")
            # Still produce an order, but mark as potentially invalid
            if not execution_order:
                execution_order = [a.id for a in actions]

        # Update action.depends_on based on resolved dependencies
        for action in actions:
            deps_for_action = [
                d.from_action_id for d in all_deps
                if d.to_action_id == action.id
            ]
            action.depends_on = list(set(deps_for_action))

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "dependencies_resolved",
            action_count=len(actions),
            dependency_count=len(all_deps),
            cycle_count=len(cycles),
            duration_ms=duration_ms,
        )

        return DependencyResolutionResult(
            execution_order=execution_order,
            dependencies=all_deps,
            cycles_detected=cycles,
            warnings=warnings,
            valid=len(cycles) == 0,
            duration_ms=duration_ms,
        )

    def _infer_dependencies(
        self,
        actions: List[ActionStep],
        action_map: Dict[str, ActionStep],
    ) -> List[Dependency]:
        """Infer implicit dependencies from action categories."""
        inferred: List[Dependency] = []

        # Group actions by category
        by_category: Dict[ActionCategory, List[ActionStep]] = {}
        for action in actions:
            if action.category not in by_category:
                by_category[action.category] = []
            by_category[action.category].append(action)

        # Apply category ordering rules
        for before_cat, after_cat in CATEGORY_ORDERING:
            before_actions = by_category.get(before_cat, [])
            after_actions = by_category.get(after_cat, [])

            for before in before_actions:
                for after in after_actions:
                    # Only add if targeting same service or no specific target
                    if (before.target_service == after.target_service or
                        before.target_service is None or
                        after.target_service is None):
                        inferred.append(Dependency(
                            from_action_id=before.id,
                            to_action_id=after.id,
                            dependency_type="recommends",
                            reason=f"Category {before_cat.value} before {after_cat.value}",
                        ))

        return inferred

    def _build_graph(
        self,
        actions: List[ActionStep],
        dependencies: List[Dependency],
    ) -> Tuple[Dict[str, List[str]], Dict[str, int]]:
        """Build adjacency list and in-degree map."""
        graph: Dict[str, List[str]] = {a.id: [] for a in actions}
        in_degree: Dict[str, int] = {a.id: 0 for a in actions}

        for dep in dependencies:
            if dep.from_action_id in graph and dep.to_action_id in in_degree:
                # Avoid duplicate edges
                if dep.to_action_id not in graph[dep.from_action_id]:
                    graph[dep.from_action_id].append(dep.to_action_id)
                    in_degree[dep.to_action_id] += 1

        return graph, in_degree

    def _topological_sort(
        self,
        actions: List[ActionStep],
        graph: Dict[str, List[str]],
        in_degree: Dict[str, int],
        action_map: Dict[str, ActionStep],
    ) -> Tuple[List[str], List[List[str]]]:
        """Perform topological sort using Kahn's algorithm."""
        # Find all nodes with no incoming edges
        queue = [aid for aid, deg in in_degree.items() if deg == 0]
        result: List[str] = []
        in_degree = dict(in_degree)  # Copy to modify

        while queue:
            # Sort by risk level (lower risk first) for deterministic ordering
            queue.sort(key=lambda x: action_map[x].risk_level.value)
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        cycles: List[List[str]] = []
        if len(result) != len(actions):
            # There are cycles - find them
            remaining = [a.id for a in actions if a.id not in result]
            cycles = self._find_cycles(remaining, graph)

        return result, cycles

    def _find_cycles(
        self,
        nodes: List[str],
        graph: Dict[str, List[str]],
    ) -> List[List[str]]:
        """Find cycles in the remaining nodes."""
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, path)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:]

            path.pop()
            rec_stack.remove(node)
            return None

        for node in nodes:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    cycles.append(cycle)

        return cycles

    def validate_order(
        self,
        actions: List[ActionStep],
        order: List[str],
    ) -> Tuple[bool, List[str]]:
        """Validate that an execution order respects all dependencies."""
        position = {aid: i for i, aid in enumerate(order)}
        violations: List[str] = []

        for action in actions:
            if action.id not in position:
                violations.append(f"Action {action.id} not in order")
                continue

            for dep_id in action.depends_on:
                if dep_id not in position:
                    continue
                if position[dep_id] >= position[action.id]:
                    violations.append(
                        f"Action {action.id} before its dependency {dep_id}"
                    )

        return len(violations) == 0, violations


def create_dependency_resolver(
    infer_implicit: bool = True,
) -> DependencyResolver:
    """Factory function to create a DependencyResolver."""
    return DependencyResolver(infer_implicit_dependencies=infer_implicit)
