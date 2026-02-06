"""
Execution Plan for Feng Shui Work Packages

Structured plan with dependencies, parallelization, and critical path.
Part of Phase 4-16: Planning with Dependencies.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum


class WorkPackageStatus(Enum):
    """Work package execution status"""
    PENDING = "pending"
    READY = "ready"  # Dependencies satisfied
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkPackageNode:
    """Work package with dependency information"""
    wp_id: str
    title: str
    description: str
    estimated_time_hours: float
    dependencies: Set[str] = field(default_factory=set)  # WP IDs this depends on
    dependents: Set[str] = field(default_factory=set)  # WPs that depend on this
    status: WorkPackageStatus = WorkPackageStatus.PENDING
    priority: int = 0  # Higher = more critical
    
    def is_ready(self, completed_wps: Set[str]) -> bool:
        """
        Check if all dependencies are satisfied
        
        Args:
            completed_wps: Set of completed work package IDs
            
        Returns:
            True if all dependencies are in completed_wps
        """
        return self.dependencies.issubset(completed_wps)
    
    def can_run_parallel_with(self, other: 'WorkPackageNode') -> bool:
        """
        Check if this WP can run in parallel with another
        
        Args:
            other: Another work package node
            
        Returns:
            True if no dependency relationship exists between the two
        """
        # True if no dependency relationship exists
        return (
            self.wp_id not in other.dependencies and
            other.wp_id not in self.dependencies and
            self.wp_id != other.wp_id
        )


@dataclass
class ExecutionPlan:
    """Structured execution plan with dependencies"""
    
    all_work_packages: List[WorkPackageNode]
    execution_order: List[str]  # Topologically sorted WP IDs
    parallel_groups: List[List[str]]  # Groups that can execute together
    critical_path: List[str]  # Longest dependency chain
    estimated_time_hours: float
    
    def visualize(self) -> str:
        """
        ASCII art visualization of execution plan
        
        Returns:
            Multi-line string with plan visualization
            
        Example output:
        ```
        Execution Plan (Est: 4.5 hours)
        ================================
        
        Sequential Tasks:
        [1] WP-001: Foundation (1h)
        
        Parallel Group 1:
        [2] WP-002: Feature A (0.5h) ||
        [3] WP-003: Feature B (1h)   ||
        [4] WP-004: Feature C (0.5h)
        
        Sequential Tasks:
        [5] WP-005: Integration (1.5h)
        
        Critical Path: WP-001 → WP-003 → WP-005 (3.5h)
        ================================
        ```
        """
        lines = []
        lines.append(f"\nExecution Plan (Est: {self.estimated_time_hours:.1f} hours)")
        lines.append("=" * 60)
        lines.append("")
        
        # Build WP lookup
        wp_by_id = {wp.wp_id: wp for wp in self.all_work_packages}
        
        # Track position in execution order
        position = 1
        processed_ids = set()
        
        # Process parallel groups
        for group_idx, group in enumerate(self.parallel_groups, 1):
            # Check if this is a sequential task or parallel group
            if len(group) == 1:
                # Sequential task
                if position == 1 or processed_ids:  # Don't add header for first task
                    if processed_ids:  # Only add header if not first
                        lines.append("Sequential Tasks:")
                
                wp_id = group[0]
                wp = wp_by_id.get(wp_id)
                if wp:
                    lines.append(f"[{position}] {wp.wp_id}: {wp.title} ({wp.estimated_time_hours:.1f}h)")
                    position += 1
                    processed_ids.add(wp_id)
                lines.append("")
            
            else:
                # Parallel group
                lines.append(f"Parallel Group {group_idx}:")
                for wp_id in group:
                    wp = wp_by_id.get(wp_id)
                    if wp:
                        lines.append(f"[{position}] {wp.wp_id}: {wp.title} ({wp.estimated_time_hours:.1f}h) ||")
                        position += 1
                        processed_ids.add(wp_id)
                lines.append("")
        
        # Show critical path
        if self.critical_path:
            critical_wps = [wp_by_id.get(wp_id) for wp_id in self.critical_path if wp_id in wp_by_id]
            if critical_wps:
                path_str = " → ".join(wp.wp_id for wp in critical_wps)
                critical_time = sum(wp.estimated_time_hours for wp in critical_wps)
                lines.append(f"Critical Path: {path_str} ({critical_time:.1f}h)")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_ready_work_packages(self, completed: Set[str]) -> List[WorkPackageNode]:
        """
        Get WPs that are ready to execute (dependencies satisfied)
        
        Args:
            completed: Set of completed work package IDs
            
        Returns:
            List of work packages ready for execution
        """
        ready = []
        for wp in self.all_work_packages:
            if wp.status == WorkPackageStatus.PENDING and wp.is_ready(completed):
                ready.append(wp)
        return ready
    
    def get_next_parallel_group(self, completed: Set[str]) -> Optional[List[WorkPackageNode]]:
        """
        Get next group of work packages that can execute in parallel
        
        Args:
            completed: Set of completed work package IDs
            
        Returns:
            List of WPs that can run in parallel, or None if no WPs ready
        """
        ready_wps = self.get_ready_work_packages(completed)
        
        if not ready_wps:
            return None
        
        # Find WPs that can run in parallel with each other
        parallel_group = [ready_wps[0]]
        
        for wp in ready_wps[1:]:
            # Check if can run in parallel with all in current group
            can_parallel = all(
                wp.can_run_parallel_with(group_wp)
                for group_wp in parallel_group
            )
            if can_parallel:
                parallel_group.append(wp)
        
        return parallel_group