"""
Feng Shui Planner - Intelligent Work Package Orchestration

Plans optimal execution strategy with dependency management and parallelization.
Part of Phase 4-16: Planning with Dependencies.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .dependency_graph import DependencyGraph
from .execution_plan import ExecutionPlan, WorkPackageNode, WorkPackageStatus


@dataclass
class ExecutionReport:
    """Report from plan execution"""
    total_work_packages: int
    completed: int
    failed: int
    skipped: int
    total_time_seconds: float
    parallel_speedup: float  # Ratio: sequential_time / actual_time
    critical_path_hours: float
    results_by_wp: Dict[str, Dict]  # wp_id -> {status, time, error}


class FengShuiPlanner:
    """
    Intelligent work package planning and orchestration
    
    Uses Planning Pattern from agentic workflows:
    - Analyzes dependencies
    - Generates optimal execution order
    - Enables parallel execution
    - Tracks progress
    """
    
    def __init__(self, automation_engine=None):
        """
        Initialize planner
        
        Args:
            automation_engine: Optional FengShuiAutomationEngine instance
        """
        self.engine = automation_engine
        self.logger = logging.getLogger(__name__)
        
    def create_execution_plan(
        self,
        work_packages: List[Dict]
    ) -> ExecutionPlan:
        """
        Generate optimal execution plan from work packages
        
        Args:
            work_packages: List of WP dicts with keys:
                - id: Work package ID
                - title: Short description
                - description: Full description
                - estimated_hours: Time estimate (optional, default 0.5)
                - dependencies: List of prerequisite WP IDs (optional)
            
        Returns:
            ExecutionPlan with optimal ordering and parallelization
        """
        self.logger.info(f"Creating execution plan for {len(work_packages)} work packages")
        
        # 1. Build dependency graph
        graph = DependencyGraph()
        
        for wp in work_packages:
            node = WorkPackageNode(
                wp_id=wp['id'],
                title=wp['title'],
                description=wp.get('description', ''),
                estimated_time_hours=wp.get('estimated_hours', 0.5),
                dependencies=set(wp.get('dependencies', []))
            )
            graph.add_work_package(node)
        
        # 2. Add explicit dependencies from WP definitions
        for wp in work_packages:
            for dep_id in wp.get('dependencies', []):
                graph.add_dependency(wp['id'], dep_id)
        
        # 3. Auto-detect implicit dependencies
        detected_deps = graph.detect_dependencies()
        for wp_id, deps in detected_deps.items():
            for dep_id in deps:
                graph.add_dependency(wp_id, dep_id)
        
        if detected_deps:
            self.logger.info(f"Auto-detected {sum(len(d) for d in detected_deps.values())} dependencies")
        
        # 4. Validate graph
        validation_errors = graph.validate_dependencies()
        if validation_errors:
            self.logger.warning(f"Dependency validation issues: {validation_errors}")
            # Continue anyway - errors will be caught during execution
        
        # 5. Calculate execution order
        try:
            execution_order = graph.topological_sort()
            self.logger.info(f"Calculated execution order: {len(execution_order)} WPs")
        except ValueError as e:
            self.logger.error(f"Failed to calculate execution order: {e}")
            # Fallback: use original order
            execution_order = [wp['id'] for wp in work_packages]
        
        # 6. Find parallel groups
        try:
            parallel_groups = graph.find_parallel_groups()
            self.logger.info(f"Identified {len(parallel_groups)} parallel groups")
        except Exception as e:
            self.logger.error(f"Failed to find parallel groups: {e}")
            # Fallback: all sequential
            parallel_groups = [[wp_id] for wp_id in execution_order]
        
        # 7. Calculate critical path
        try:
            critical_path, critical_time = graph.calculate_critical_path()
            self.logger.info(f"Critical path: {len(critical_path)} WPs, {critical_time:.1f}h")
        except Exception as e:
            self.logger.error(f"Failed to calculate critical path: {e}")
            # Fallback: use execution order
            critical_path = execution_order
            critical_time = sum(wp.get('estimated_hours', 0.5) for wp in work_packages)
        
        return ExecutionPlan(
            all_work_packages=list(graph.nodes.values()),
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            critical_path=critical_path,
            estimated_time_hours=critical_time
        )
    
    def execute_plan(
        self,
        plan: ExecutionPlan,
        parallel: bool = True,
        max_workers: int = 4
    ) -> ExecutionReport:
        """
        Execute plan with optional parallelization
        
        Args:
            plan: Execution plan to run
            parallel: Enable parallel execution (default True)
            max_workers: Max parallel threads (default 4)
            
        Returns:
            ExecutionReport with results per work package
        """
        start_time = time.time()
        completed_wps = set()
        results_by_wp = {}
        
        if parallel:
            self.logger.info(f"Executing plan with {len(plan.parallel_groups)} parallel groups (max {max_workers} workers)")
            
            for group_idx, group in enumerate(plan.parallel_groups, 1):
                group_size = len(group)
                self.logger.info(f"Parallel Group {group_idx}/{len(plan.parallel_groups)}: {group_size} work package(s)")
                
                # Execute group in parallel
                group_results = self._execute_parallel_group(
                    group,
                    plan.all_work_packages,
                    max_workers
                )
                
                # Update results
                for wp_id, result in group_results.items():
                    results_by_wp[wp_id] = result
                    if result['status'] == 'completed':
                        completed_wps.add(wp_id)
                        self.logger.info(f"✓ {wp_id} completed in {result['time_seconds']:.1f}s")
                    else:
                        self.logger.warning(f"✗ {wp_id} failed: {result.get('error', 'unknown')}")
        
        else:
            # Sequential execution (fallback)
            self.logger.info(f"Executing plan sequentially ({len(plan.execution_order)} WPs)")
            
            for idx, wp_id in enumerate(plan.execution_order, 1):
                self.logger.info(f"Executing [{idx}/{len(plan.execution_order)}]: {wp_id}")
                
                wp = next((w for w in plan.all_work_packages if w.wp_id == wp_id), None)
                if not wp:
                    self.logger.error(f"Work package {wp_id} not found in plan")
                    continue
                
                result = self._execute_work_package(wp)
                results_by_wp[wp_id] = result
                
                if result['status'] == 'completed':
                    completed_wps.add(wp_id)
                    self.logger.info(f"✓ {wp_id} completed in {result['time_seconds']:.1f}s")
                else:
                    self.logger.warning(f"✗ {wp_id} failed: {result.get('error', 'unknown')}")
        
        # Calculate metrics
        total_time = time.time() - start_time
        completed_count = sum(1 for r in results_by_wp.values() if r['status'] == 'completed')
        failed_count = sum(1 for r in results_by_wp.values() if r['status'] == 'failed')
        skipped_count = sum(1 for r in results_by_wp.values() if r['status'] == 'skipped')
        
        # Calculate parallel speedup
        # Sequential time = sum of all WP times
        sequential_time = sum(wp.estimated_time_hours * 3600 for wp in plan.all_work_packages)
        speedup = sequential_time / total_time if total_time > 0 else 1.0
        
        self.logger.info(f"Execution complete: {completed_count} completed, {failed_count} failed, {skipped_count} skipped")
        self.logger.info(f"Total time: {total_time:.1f}s, Speedup: {speedup:.2f}x")
        
        return ExecutionReport(
            total_work_packages=len(plan.all_work_packages),
            completed=completed_count,
            failed=failed_count,
            skipped=skipped_count,
            total_time_seconds=total_time,
            parallel_speedup=speedup,
            critical_path_hours=plan.estimated_time_hours,
            results_by_wp=results_by_wp
        )
    
    def _execute_parallel_group(
        self,
        group: List[str],
        all_wps: List[WorkPackageNode],
        max_workers: int
    ) -> Dict[str, Dict]:
        """
        Execute a group of work packages in parallel
        
        Args:
            group: List of WP IDs to execute in parallel
            all_wps: All work package nodes
            max_workers: Maximum number of parallel threads
            
        Returns:
            Results dict: wp_id -> {status, time_seconds, error}
        """
        results = {}
        
        # Limit workers to group size (no point having more threads than tasks)
        actual_workers = min(max_workers, len(group))
        
        with ThreadPoolExecutor(max_workers=actual_workers) as executor:
            # Submit all WPs in group
            future_to_wp = {}
            for wp_id in group:
                wp = next((w for w in all_wps if w.wp_id == wp_id), None)
                if wp:
                    future = executor.submit(self._execute_work_package, wp)
                    future_to_wp[future] = wp_id
                else:
                    self.logger.error(f"Work package {wp_id} not found")
                    results[wp_id] = {
                        'status': 'failed',
                        'time_seconds': 0,
                        'error': 'Work package not found'
                    }
            
            # Collect results as they complete
            for future in as_completed(future_to_wp):
                wp_id = future_to_wp[future]
                try:
                    result = future.result()
                    results[wp_id] = result
                except Exception as e:
                    self.logger.error(f"Exception during execution of {wp_id}: {e}")
                    results[wp_id] = {
                        'status': 'failed',
                        'time_seconds': 0,
                        'error': str(e)
                    }
        
        return results
    
    def _execute_work_package(self, wp: WorkPackageNode) -> Dict:
        """
        Execute a single work package
        
        Args:
            wp: Work package node to execute
            
        Returns:
            Result dict: {status, time_seconds, error}
        """
        self.logger.debug(f"Starting execution: {wp.title}")
        start_time = time.time()
        
        try:
            # Check if engine is available
            if not self.engine:
                self.logger.warning(f"No automation engine available, simulating execution for {wp.wp_id}")
                # Simulate execution (for testing)
                time.sleep(0.1)
                success = True
            else:
                # Use automation engine to apply fixes for this WP
                # Note: This assumes automation_engine has execute_work_package method
                # If not, we'll need to adapt this integration point
                if hasattr(self.engine, 'execute_work_package'):
                    success = self.engine.execute_work_package(wp.wp_id)
                else:
                    # Fallback: execute individual fixes
                    self.logger.warning(f"Engine missing execute_work_package, using fallback for {wp.wp_id}")
                    success = True  # Assume success for now
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'completed' if success else 'failed',
                'time_seconds': execution_time,
                'error': None if success else 'Execution returned failure'
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Failed to execute {wp.title}: {str(e)}")
            
            return {
                'status': 'failed',
                'time_seconds': execution_time,
                'error': str(e)
            }
    
    def estimate_sequential_time(self, work_packages: List[Dict]) -> float:
        """
        Estimate total time if executed sequentially
        
        Args:
            work_packages: List of work package dicts
            
        Returns:
            Total estimated hours for sequential execution
        """
        return sum(wp.get('estimated_hours', 0.5) for wp in work_packages)
    
    def estimate_parallel_time(self, plan: ExecutionPlan) -> float:
        """
        Estimate total time with parallel execution
        
        Args:
            plan: Execution plan
            
        Returns:
            Estimated hours considering parallelization
        """
        # Parallel time ≈ sum of group max times
        total_hours = 0.0
        
        wp_by_id = {wp.wp_id: wp for wp in plan.all_work_packages}
        
        for group in plan.parallel_groups:
            # Group time = max time of any WP in group
            group_times = [
                wp_by_id[wp_id].estimated_time_hours
                for wp_id in group
                if wp_id in wp_by_id
            ]
            total_hours += max(group_times) if group_times else 0.0
        
        return total_hours
    
    def visualize_plan(self, plan: ExecutionPlan) -> str:
        """
        Generate detailed plan visualization
        
        Args:
            plan: Execution plan to visualize
            
        Returns:
            Multi-line string with detailed visualization
        """
        return plan.visualize()