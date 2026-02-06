"""
Dependency Graph for Feng Shui Work Packages

Automatically detects dependencies and calculates optimal execution order.
Part of Phase 4-16: Planning with Dependencies.
"""

from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from enum import Enum
import logging

from .execution_plan import WorkPackageNode, WorkPackageStatus


class DependencyType(Enum):
    """Types of dependencies between work packages"""
    PREREQUISITE = "prerequisite"  # Must complete before
    CONFLICTS_WITH = "conflicts_with"  # Cannot run simultaneously
    ENHANCES = "enhances"  # Better if run after, but not required


class DependencyGraph:
    """
    Manage work package dependencies and execution order
    
    Features:
    - Automatic dependency detection (rule-based)
    - Topological sort for optimal ordering
    - Parallel group identification
    - Critical path analysis (longest chain)
    """
    
    def __init__(self):
        self.nodes: Dict[str, WorkPackageNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # wp_id -> set of dependencies
        self.logger = logging.getLogger(__name__)
        
    def add_work_package(self, wp: WorkPackageNode):
        """
        Add work package to graph
        
        Args:
            wp: Work package node to add
        """
        self.nodes[wp.wp_id] = wp
        if wp.wp_id not in self.edges:
            self.edges[wp.wp_id] = set()
    
    def add_dependency(self, from_wp: str, to_wp: str):
        """
        Add dependency: from_wp depends on to_wp
        
        Args:
            from_wp: Work package that has the dependency
            to_wp: Work package that must complete first
        """
        if from_wp in self.edges:
            self.edges[from_wp].add(to_wp)
        else:
            self.edges[from_wp] = {to_wp}
        
        # Update node objects
        if from_wp in self.nodes and to_wp in self.nodes:
            self.nodes[from_wp].dependencies.add(to_wp)
            self.nodes[to_wp].dependents.add(from_wp)
    
    def detect_dependencies(self) -> Dict[str, Set[str]]:
        """
        Automatically detect dependencies based on rules
        
        Rules:
        1. Interface changes → Implementation changes
        2. module.json creation → Blueprint configuration
        3. Test creation → Coverage validation
        4. Schema changes → Migration scripts
        5. File moves → Import updates
        
        Returns:
            Detected dependencies (wp_id -> set of prerequisite wp_ids)
        """
        detected = {}
        
        for wp_id, wp in self.nodes.items():
            prerequisites = set()
            
            # Rule 1: Interface changes must come before implementations
            if 'implementation' in wp.description.lower() or 'implement' in wp.title.lower():
                for other_id, other_wp in self.nodes.items():
                    if wp_id != other_id and ('interface' in other_wp.description.lower() or 'interface' in other_wp.title.lower()):
                        prerequisites.add(other_id)
                        self.logger.debug(f"Detected dependency: {wp_id} depends on {other_id} (interface→impl)")
            
            # Rule 2: module.json must exist before blueprint config
            if 'blueprint' in wp.description.lower() or 'blueprint' in wp.title.lower():
                for other_id, other_wp in self.nodes.items():
                    if wp_id != other_id and 'module.json' in other_wp.description.lower():
                        prerequisites.add(other_id)
                        self.logger.debug(f"Detected dependency: {wp_id} depends on {other_id} (module.json→blueprint)")
            
            # Rule 3: Tests must exist before coverage checks
            if 'coverage' in wp.description.lower() or 'test validation' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if wp_id != other_id:
                        # Check if it's a test creation WP (not coverage/validation)
                        is_test_creation = (
                            'test' in other_wp.title.lower() and
                            'coverage' not in other_wp.title.lower() and
                            'validation' not in other_wp.title.lower()
                        )
                        if is_test_creation:
                            prerequisites.add(other_id)
                            self.logger.debug(f"Detected dependency: {wp_id} depends on {other_id} (test→coverage)")
            
            # Rule 4: Schema changes before migrations
            if 'migration' in wp.description.lower() or 'migrate' in wp.title.lower() or 'migrate' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if wp_id != other_id and ('schema' in other_wp.description.lower() or 'schema' in other_wp.title.lower()):
                        prerequisites.add(other_id)
                        self.logger.debug(f"Detected dependency: {wp_id} depends on {other_id} (schema→migration)")
            
            # Rule 5: File operations before imports
            if 'import' in wp.description.lower() or 'reference' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if wp_id != other_id:
                        if 'move' in other_wp.description.lower() or 'rename' in other_wp.description.lower():
                            prerequisites.add(other_id)
                            self.logger.debug(f"Detected dependency: {wp_id} depends on {other_id} (file-op→import)")
            
            if prerequisites:
                detected[wp_id] = prerequisites
        
        return detected
    
    def topological_sort(self) -> List[str]:
        """
        Calculate optimal execution order using Kahn's algorithm
        
        Returns:
            Ordered list of WP IDs respecting all dependencies
            
        Raises:
            ValueError: If circular dependency detected
        """
        # Calculate in-degree (number of dependencies) for each node
        in_degree = {wp_id: len(deps) for wp_id, deps in self.edges.items()}
        
        # Ensure all nodes are in in_degree (even if no dependencies)
        for wp_id in self.nodes:
            if wp_id not in in_degree:
                in_degree[wp_id] = 0
        
        # Queue nodes with no dependencies
        queue = [wp_id for wp_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort queue by priority (higher priority first)
            queue.sort(key=lambda wp_id: self.nodes[wp_id].priority, reverse=True)
            
            # Process highest priority WP with no dependencies
            wp_id = queue.pop(0)
            result.append(wp_id)
            
            # Update dependents (reduce their in-degree)
            if wp_id in self.nodes:
                for dependent_id in self.nodes[wp_id].dependents:
                    if dependent_id in in_degree:
                        in_degree[dependent_id] -= 1
                        if in_degree[dependent_id] == 0:
                            queue.append(dependent_id)
        
        # Check for cycles
        if len(result) != len(self.nodes):
            unprocessed = set(self.nodes.keys()) - set(result)
            raise ValueError(f"Circular dependency detected. Unprocessed WPs: {unprocessed}")
        
        return result
    
    def find_parallel_groups(self) -> List[List[str]]:
        """
        Identify work packages that can execute in parallel
        
        Algorithm:
        1. Start with topologically sorted order
        2. Group WPs at same "level" (no dependencies between them)
        3. Return groups that can run simultaneously
        
        Returns:
            List of parallel groups (list of WP IDs)
        """
        sorted_wps = self.topological_sort()
        groups = []
        processed = set()
        
        while len(processed) < len(sorted_wps):
            current_group = []
            
            for wp_id in sorted_wps:
                if wp_id in processed:
                    continue
                
                # Check if all dependencies satisfied
                wp = self.nodes[wp_id]
                if wp.dependencies.issubset(processed):
                    # Check if can run in parallel with current group
                    can_parallel = all(
                        self.nodes[wp_id].can_run_parallel_with(self.nodes[other_id])
                        for other_id in current_group
                    )
                    
                    if can_parallel or not current_group:
                        current_group.append(wp_id)
            
            if current_group:
                groups.append(current_group)
                processed.update(current_group)
            else:
                # Safety: No more WPs can be processed
                break
        
        return groups
    
    def calculate_critical_path(self) -> Tuple[List[str], float]:
        """
        Find longest dependency chain (critical path)
        
        Uses dynamic programming to find path with maximum total time.
        This is the bottleneck that determines minimum execution time.
        
        Returns:
            Tuple of (WP IDs in critical path, total estimated hours)
        """
        # Build memo for DP: wp_id -> (max_time, path)
        memo: Dict[str, Tuple[float, List[str]]] = {}
        
        def find_longest_path(wp_id: str) -> Tuple[float, List[str]]:
            """Recursive DP to find longest path from wp_id"""
            # Base case: already computed
            if wp_id in memo:
                return memo[wp_id]
            
            wp = self.nodes[wp_id]
            
            # Base case: no dependents (leaf node)
            if not wp.dependents:
                memo[wp_id] = (wp.estimated_time_hours, [wp_id])
                return memo[wp_id]
            
            # Recursive case: find longest path through dependents
            max_time = 0.0
            max_path = []
            
            for dependent_id in wp.dependents:
                dependent_time, dependent_path = find_longest_path(dependent_id)
                if dependent_time > max_time:
                    max_time = dependent_time
                    max_path = dependent_path
            
            # Add current WP to path
            total_time = wp.estimated_time_hours + max_time
            full_path = [wp_id] + max_path
            
            memo[wp_id] = (total_time, full_path)
            return memo[wp_id]
        
        # Find longest path starting from any node
        max_critical_time = 0.0
        critical_path = []
        
        # Check all nodes as potential starting points
        for wp_id in self.nodes:
            path_time, path = find_longest_path(wp_id)
            if path_time > max_critical_time:
                max_critical_time = path_time
                critical_path = path
        
        return (critical_path, max_critical_time)
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate dependency graph for issues
        
        Checks:
        - Circular dependencies
        - Missing work packages
        - Orphaned dependencies
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for circular dependencies
        try:
            self.topological_sort()
        except ValueError as e:
            errors.append(f"Circular dependency: {str(e)}")
        
        # Check for missing WPs
        for wp_id, deps in self.edges.items():
            for dep_id in deps:
                if dep_id not in self.nodes:
                    errors.append(f"Missing dependency: {wp_id} depends on non-existent {dep_id}")
        
        # Check for orphaned dependencies in nodes
        for wp_id, wp in self.nodes.items():
            for dep_id in wp.dependencies:
                if dep_id not in self.nodes:
                    errors.append(f"Orphaned dependency in node: {wp_id} depends on non-existent {dep_id}")
        
        return errors
    
    def get_dependency_depth(self, wp_id: str) -> int:
        """
        Calculate dependency depth (how many levels of dependencies)
        
        Args:
            wp_id: Work package ID
            
        Returns:
            Maximum depth of dependency chain for this WP
        """
        if wp_id not in self.nodes:
            return 0
        
        wp = self.nodes[wp_id]
        
        if not wp.dependencies:
            return 0
        
        # Recursive depth calculation
        max_depth = 0
        for dep_id in wp.dependencies:
            depth = self.get_dependency_depth(dep_id)
            max_depth = max(max_depth, depth + 1)
        
        return max_depth
    
    def get_independent_work_packages(self) -> List[str]:
        """
        Get work packages with no dependencies (can start immediately)
        
        Returns:
            List of WP IDs with no dependencies
        """
        return [
            wp_id for wp_id, wp in self.nodes.items()
            if not wp.dependencies
        ]
    
    def get_dependency_tree(self, wp_id: str) -> Dict:
        """
        Get full dependency tree for a work package
        
        Args:
            wp_id: Work package ID
            
        Returns:
            Tree structure showing all dependencies recursively
        """
        if wp_id not in self.nodes:
            return {}
        
        wp = self.nodes[wp_id]
        
        tree = {
            'wp_id': wp_id,
            'title': wp.title,
            'dependencies': []
        }
        
        for dep_id in wp.dependencies:
            tree['dependencies'].append(self.get_dependency_tree(dep_id))
        
        return tree