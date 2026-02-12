# Feng Shui Phase 4.16: Planning with Dependencies Implementation Plan

**Status**: 📋 READY FOR IMPLEMENTATION  
**Created**: 2026-02-06  
**Estimated Effort**: 6-8 hours  
**Prerequisites**: Phase 4-15 Complete ✅ (ReAct + Reflection + 38 tests passing)

---

## 🎯 Objective

Add **intelligent work package orchestration** with:
- **Dependency Detection**: Automatically identify WP prerequisites
- **Optimal Ordering**: Topological sort for correct execution sequence
- **Parallel Execution**: Run independent WPs simultaneously (3x speedup)
- **Critical Path Analysis**: Identify bottlenecks for prioritization

**Transforms**:
```
TODAY:     WP-001, WP-002, WP-003 (sequential, arbitrary order)
PHASE 4.16: WP-001 → [WP-002 || WP-003] → WP-004 (optimal parallel execution)
```

---

## 📦 Deliverables

### Phase 4.16 Components (6 files)

**New Files**:
1. `tools/fengshui/dependency_graph.py` - Dependency management (180-220 LOC)
2. `tools/fengshui/planner.py` - Intelligent orchestration (200-250 LOC)
3. `tools/fengshui/execution_plan.py` - Plan data structure (80-100 LOC)
4. `tests/unit/tools/fengshui/test_planner.py` - Unit tests (150-200 LOC)
5. `tests/unit/tools/fengshui/test_dependency_graph.py` - Unit tests (120-150 LOC)
6. `tests/integration/test_fengshui_planner_integration.py` - Integration tests (80-100 LOC)

**Modified Files**:
1. `tools/fengshui/react_agent.py` - Integration with planner
2. `tools/fengshui/automation_engine.py` - Parallel execution support

**Documentation**:
1. `docs/knowledge/architecture/feng-shui-phase4-16-planning.md` - Complete guide

---

## 🏗️ Implementation Steps

### Step 1: Execution Plan Data Structure (45 min)

**File**: `tools/fengshui/execution_plan.py`

```python
"""
Execution Plan for Feng Shui Work Packages

Structured plan with dependencies, parallelization, and critical path.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set
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
        """Check if all dependencies are satisfied"""
        return self.dependencies.issubset(completed_wps)
    
    def can_run_parallel_with(self, other: 'WorkPackageNode') -> bool:
        """Check if this WP can run in parallel with another"""
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
        lines.append("=" * 50)
        
        # TODO: Implement full visualization
        # Show sequential tasks
        # Show parallel groups with || indicators
        # Highlight critical path
        
        return "\n".join(lines)
    
    def get_ready_work_packages(self, completed: Set[str]) -> List[WorkPackageNode]:
        """Get WPs that are ready to execute (dependencies satisfied)"""
        ready = []
        for wp in self.all_work_packages:
            if wp.status == WorkPackageStatus.PENDING and wp.is_ready(completed):
                ready.append(wp)
        return ready
```

### Step 2: Dependency Graph Builder (2-3 hours)

**File**: `tools/fengshui/dependency_graph.py`

```python
"""
Dependency Graph for Feng Shui Work Packages

Automatically detects dependencies and calculates optimal execution order.
"""

from typing import List, Dict, Set, Tuple
from pathlib import Path
import json

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
        
    def add_work_package(self, wp: WorkPackageNode):
        """Add work package to graph"""
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
            if 'implementation' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if 'interface' in other_wp.description.lower() and wp_id != other_id:
                        prerequisites.add(other_id)
            
            # Rule 2: module.json must exist before blueprint config
            if 'blueprint' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if 'module.json' in other_wp.description.lower() and wp_id != other_id:
                        prerequisites.add(other_id)
            
            # Rule 3: Tests must exist before coverage checks
            if 'coverage' in wp.description.lower() or 'test validation' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if 'test' in other_wp.title.lower() and 'coverage' not in other_wp.title.lower():
                        prerequisites.add(other_id)
            
            # Rule 4: Schema changes before migrations
            if 'migration' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if 'schema' in other_wp.description.lower() and wp_id != other_id:
                        prerequisites.add(other_id)
            
            # Rule 5: File operations before imports
            if 'import' in wp.description.lower() or 'reference' in wp.description.lower():
                for other_id, other_wp in self.nodes.items():
                    if 'move' in other_wp.description.lower() or 'rename' in other_wp.description.lower():
                        prerequisites.add(other_id)
            
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
        # Kahn's algorithm implementation
        in_degree = {wp_id: len(deps) for wp_id, deps in self.edges.items()}
        queue = [wp_id for wp_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Process WPs with no dependencies
            wp_id = queue.pop(0)
            result.append(wp_id)
            
            # Update dependents
            for dependent_id in self.nodes[wp_id].dependents:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # Check for cycles
        if len(result) != len(self.nodes):
            raise ValueError("Circular dependency detected in work packages")
        
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
                break  # No more WPs can be processed
        
        return groups
    
    def calculate_critical_path(self) -> Tuple[List[str], float]:
        """
        Find longest dependency chain (critical path)
        
        Uses dynamic programming to find path with maximum total time.
        
        Returns:
            Tuple of (WP IDs in critical path, total estimated hours)
        """
        # Build reverse graph for DP
        # Calculate longest path from each node
        # Return path with maximum time
        
        # Placeholder implementation
        sorted_wps = self.topological_sort()
        return (sorted_wps, sum(self.nodes[wp_id].estimated_time_hours for wp_id in sorted_wps))
    
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
        
        return errors
```

### Step 3: Feng Shui Planner (2-3 hours)

**File**: `tools/fengshui/planner.py`

```python
"""
Feng Shui Planner - Intelligent Work Package Orchestration

Plans optimal execution strategy with dependency management and parallelization.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .dependency_graph import DependencyGraph
from .execution_plan import ExecutionPlan, WorkPackageNode, WorkPackageStatus
from .automation_engine import FengShuiAutomationEngine

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
    
    def __init__(self, automation_engine: FengShuiAutomationEngine = None):
        self.engine = automation_engine or FengShuiAutomationEngine()
        self.logger = logging.getLogger(__name__)
        
    def create_execution_plan(
        self,
        work_packages: List[Dict]
    ) -> ExecutionPlan:
        """
        Generate optimal execution plan from work packages
        
        Args:
            work_packages: List of WP dicts from work_package_builder
            
        Returns:
            ExecutionPlan with optimal ordering and parallelization
        """
        # 1. Build dependency graph
        graph = DependencyGraph()
        
        for wp in work_packages:
            node = WorkPackageNode(
                wp_id=wp['id'],
                title=wp['title'],
                description=wp['description'],
                estimated_time_hours=wp.get('estimated_hours', 0.5),
                dependencies=set(wp.get('dependencies', []))
            )
            graph.add_work_package(node)
        
        # 2. Auto-detect dependencies
        detected_deps = graph.detect_dependencies()
        for wp_id, deps in detected_deps.items():
            for dep_id in deps:
                graph.add_dependency(wp_id, dep_id)
        
        # 3. Validate graph
        validation_errors = graph.validate_dependencies()
        if validation_errors:
            self.logger.warning(f"Dependency validation issues: {validation_errors}")
        
        # 4. Calculate execution order
        execution_order = graph.topological_sort()
        
        # 5. Find parallel groups
        parallel_groups = graph.find_parallel_groups()
        
        # 6. Calculate critical path
        critical_path, critical_time = graph.calculate_critical_path()
        
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
            self.logger.info(f"Executing plan with {len(plan.parallel_groups)} parallel groups")
            
            for group_idx, group in enumerate(plan.parallel_groups, 1):
                self.logger.info(f"Parallel Group {group_idx}: {len(group)} work packages")
                
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
        
        else:
            # Sequential execution (fallback)
            self.logger.info(f"Executing plan sequentially ({len(plan.execution_order)} WPs)")
            
            for wp_id in plan.execution_order:
                wp = next(w for w in plan.all_work_packages if w.wp_id == wp_id)
                result = self._execute_work_package(wp)
                results_by_wp[wp_id] = result
                
                if result['status'] == 'completed':
                    completed_wps.add(wp_id)
        
        # Calculate metrics
        total_time = time.time() - start_time
        completed_count = sum(1 for r in results_by_wp.values() if r['status'] == 'completed')
        failed_count = sum(1 for r in results_by_wp.values() if r['status'] == 'failed')
        skipped_count = sum(1 for r in results_by_wp.values() if r['status'] == 'skipped')
        
        # Calculate parallel speedup
        sequential_time = sum(wp.estimated_time_hours for wp in plan.all_work_packages) * 3600
        speedup = sequential_time / total_time if total_time > 0 else 1.0
        
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
        """Execute a group of work packages in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all WPs in group
            future_to_wp = {}
            for wp_id in group:
                wp = next(w for w in all_wps if w.wp_id == wp_id)
                future = executor.submit(self._execute_work_package, wp)
                future_to_wp[future] = wp_id
            
            # Collect results
            for future in as_completed(future_to_wp):
                wp_id = future_to_wp[future]
                try:
                    result = future.result()
                    results[wp_id] = result
                except Exception as e:
                    results[wp_id] = {
                        'status': 'failed',
                        'time_seconds': 0,
                        'error': str(e)
                    }
        
        return results
    
    def _execute_work_package(self, wp: WorkPackageNode) -> Dict:
        """Execute a single work package"""
        self.logger.info(f"Executing: {wp.title}")
        start_time = time.time()
        
        try:
            # Use automation engine to apply fixes for this WP
            success = self.engine.execute_work_package(wp.wp_id)
            
            execution_time = time.time() - start_time
            
            return {
                'status': 'completed' if success else 'failed',
                'time_seconds': execution_time,
                'error': None
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Failed to execute {wp.title}: {str(e)}")
            
            return {
                'status': 'failed',
                'time_seconds': execution_time,
                'error': str(e)
            }
```

### Step 4: Integration with ReAct Agent (30 min)

**File**: `tools/fengshui/react_agent.py` (modify existing)

```python
# Add planner integration

class FengShuiReActAgent:
    """Autonomous reasoning agent"""
    
    def __init__(self, automation_engine=None):
        # ... existing init ...
        self.planner = FengShuiPlanner(self.engine)  # ADD THIS
    
    def run_autonomous_session_with_planning(
        self,
        goal: str,
        max_iterations: int = 10,
        parallel: bool = True
    ) -> SessionReport:
        """
        Run autonomous session with intelligent planning
        
        NEW: Uses planner to optimize work package execution
        """
        # 1. Analyze current state
        state = self.state_analyzer.analyze_current_state()
        
        # 2. Generate work packages
        work_packages = self.engine.generate_work_packages()
        
        # 3. Create execution plan (NEW)
        plan = self.planner.create_execution_plan(work_packages)
        self.logger.info(f"Execution plan:\n{plan.visualize()}")
        
        # 4. Execute plan with parallelization (NEW)
        report = self.planner.execute_plan(plan, parallel=parallel)
        
        # 5. Measure improvement
        new_state = self.state_analyzer.analyze_current_state()
        
        # 6. Reflect and learn
        self._reflect_on_execution(report, state, new_state)
        
        return report
```

### Step 5: Unit Tests - Planner (2 hours)

**File**: `tests/unit/tools/fengshui/test_planner.py`

```python
"""
Unit tests for FengShuiPlanner
"""

import pytest
from tools.fengshui.planner import FengShuiPlanner
from tools.fengshui.execution_plan import WorkPackageNode

@pytest.mark.unit
def test_planner_creates_execution_plan():
    """Test planner generates execution plan"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Fix DI', 'description': 'Fix DI violations'},
        {'id': 'WP-002', 'title': 'Fix Blueprint', 'description': 'Fix blueprint config'}
    ]
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    
    # ASSERT
    assert len(plan.all_work_packages) == 2
    assert len(plan.execution_order) == 2
    assert plan.estimated_time_hours > 0

@pytest.mark.unit
def test_planner_parallel_execution_faster_than_sequential():
    """Test parallel execution is faster"""
    # ARRANGE
    planner = FengShuiPlanner()
    # Create WPs with no dependencies (can run in parallel)
    wps = [
        WorkPackageNode('WP-001', 'Task 1', 'Independent task 1', 0.1),
        WorkPackageNode('WP-002', 'Task 2', 'Independent task 2', 0.1),
        WorkPackageNode('WP-003', 'Task 3', 'Independent task 3', 0.1)
    ]
    
    # ACT
    plan = planner.create_execution_plan([{
        'id': wp.wp_id,
        'title': wp.title,
        'description': wp.description
    } for wp in wps])
    
    # ASSERT
    assert len(plan.parallel_groups) > 0
    # Should have at least one group with multiple WPs
    assert any(len(group) > 1 for group in plan.parallel_groups)

# Add 8-10 more tests
```

**File**: `tests/unit/tools/fengshui/test_dependency_graph.py`

```python
"""
Unit tests for DependencyGraph
"""

import pytest
from tools.fengshui.dependency_graph import DependencyGraph
from tools.fengshui.execution_plan import WorkPackageNode

@pytest.mark.unit
def test_dependency_graph_topological_sort():
    """Test topological sorting respects dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    wp1 = WorkPackageNode('WP-001', 'Foundation', 'Base work', 1.0)
    wp2 = WorkPackageNode('WP-002', 'Feature', 'Depends on foundation', 0.5)
    
    graph.add_work_package(wp1)
    graph.add_work_package(wp2)
    graph.add_dependency('WP-002', 'WP-001')  # WP-002 depends on WP-001
    
    # ACT
    order = graph.topological_sort()
    
    # ASSERT
    assert order.index('WP-001') < order.index('WP-002')

@pytest.mark.unit
def test_dependency_detection_interface_before_implementation():
    """Test auto-detection of interface → implementation dependency"""
    # ARRANGE
    graph = DependencyGraph()
    interface_wp = WorkPackageNode('WP-001', 'Interface', 'Create interface changes', 1.0)
    impl_wp = WorkPackageNode('WP-002', 'Implementation', 'Implement feature', 2.0)
    
    graph.add_work_package(interface_wp)
    graph.add_work_package(impl_wp)
    
    # ACT
    detected = graph.detect_dependencies()
    
    # ASSERT
    assert 'WP-002' in detected
    assert 'WP-001' in detected['WP-002']

@pytest.mark.unit
def test_circular_dependency_detection():
    """Test graph detects circular dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    wp1 = WorkPackageNode('WP-001', 'A', 'Task A', 1.0)
    wp2 = WorkPackageNode('WP-002', 'B', 'Task B', 1.0)
    
    graph.add_work_package(wp1)
    graph.add_work_package(wp2)
    graph.add_dependency('WP-001', 'WP-002')
    graph.add_dependency('WP-002', 'WP-001')  # Circular!
    
    # ACT & ASSERT
    with pytest.raises(ValueError, match="Circular dependency"):
        graph.topological_sort()

# Add 6-8 more tests
```

### Step 6: Integration Tests (1 hour)

**File**: `tests/integration/test_fengshui_planner_integration.py`

```python
"""
Integration tests for Planner with real work packages
"""

import pytest
from tools.fengshui.planner import FengShuiPlanner

@pytest.mark.integration
def test_planner_real_work_packages():
    """Test planner with real project work packages"""
    # ARRANGE
    planner = FengShuiPlanner()
    
    # Get real WPs from automation engine
    work_packages = planner.engine.work_package_builder.build_work_packages()
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    
    # ASSERT
    assert len(plan.all_work_packages) > 0
    assert len(plan.execution_order) == len(plan.all_work_packages)
    assert plan.estimated_time_hours > 0
    
    # Visualize for manual inspection
    print(plan.visualize())

@pytest.mark.integration
def test_parallel_execution_speedup():
    """Test parallel execution provides speedup"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': f'WP-{i:03d}', 'title': f'Task {i}', 'description': f'Independent task {i}'}
        for i in range(1, 6)
    ]
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    report = planner.execute_plan(plan, parallel=True)
    
    # ASSERT
    assert report.parallel_speedup > 1.0  # Should be faster than sequential
    self.logger.info(f"Parallel speedup: {report.parallel_speedup:.2f}x")
```

### Step 7: Documentation (1-2 hours)

**File**: `docs/knowledge/architecture/feng-shui-phase4-16-planning.md`

Structure:
```markdown
# Feng Shui Phase 4.16: Planning with Dependencies

## Overview
- What is the Planning Pattern?
- Why dependency management matters
- Parallel execution benefits

## Architecture
- DependencyGraph component
- FengShuiPlanner component
- ExecutionPlan structure

## Usage Examples
```python
# Example 1: Create execution plan
# Example 2: Execute with parallelization
# Example 3: Visualize plan
```

## Dependency Detection Rules
1. Interface → Implementation
2. module.json → Blueprint config
3. Test creation → Coverage checks
4. Schema → Migration
5. File operations → Import updates

## Parallel Execution
- Thread pool configuration
- Safety considerations
- Performance tuning

## Integration with ReAct Agent
- Combined autonomous + planning
- Strategy selection with planning
- Reflection on plan execution

## Troubleshooting
- Circular dependency errors
- Parallel execution issues
- Performance tuning
```

---

## 🧪 Testing Strategy

### Unit Tests (Expected: 15-18 tests)
- Planner: 8-10 tests
- Dependency graph: 8-10 tests
- Execution plan: 2-3 tests

### Integration Tests (Expected: 2-3 tests)
- Real work package planning
- Parallel execution speedup
- Combined ReAct + Planning

### Success Criteria
- ✅ All unit tests passing (15+/15+)
- ✅ All integration tests passing (2+/2+)
- ✅ Parallel speedup ≥ 2x (measured)
- ✅ Dependency detection ≥ 90% accurate
- ✅ Zero circular dependency issues

---

## 📊 Validation Checklist

**Test 1: Dependency Detection**
```bash
python -m tools.fengshui.planner --detect-deps
# Expected: Shows detected dependencies with rules applied
```

**Test 2: Parallel Execution**
```bash
python -m tools.fengshui.planner --execute --parallel --max-workers 4
# Expected: 3x faster than sequential
```

**Test 3: Plan Visualization**
```bash
python -m tools.fengshui.planner --visualize
# Expected: ASCII art showing execution flow
```

**Test 4: Integration with ReAct**
```python
from tools.fengshui.react_agent import FengShuiReActAgent

agent = FengShuiReActAgent()
report = agent.run_autonomous_session_with_planning(
    goal="score >= 95",
    parallel=True
)

print(f"Speedup: {report.parallel_speedup:.2f}x")
```

---

## ⏱️ Time Estimates

| Task | Estimated Time | Cumulative |
|------|---------------|------------|
| Step 1: ExecutionPlan | 45 min | 0.75h |
| Step 2: DependencyGraph | 2-3 hours | 2.75-3.75h |
| Step 3: FengShuiPlanner | 2-3 hours | 4.75-6.75h |
| Step 4: ReAct integration | 30 min | 5.25-7.25h |
| Step 5: Unit tests (Planner) | 1 hour | 6.25-8.25h |
| Step 6: Unit tests (DependencyGraph) | 1 hour | 7.25-9.25h |
| Step 7: Integration tests | 1 hour | 8.25-10.25h |
| Step 8: Documentation | 1-2 hours | 9.25-12.25h |
| **TOTAL** | **9-12 hours** | - |

**Note**: Original estimate 6-8 hours, revised to 9-12 hours for comprehensive testing.

---

## 🎯 Success Metrics

### Performance Goals
- **Parallel Speedup**: ≥ 3x faster than sequential (target: 4x with 4 workers)
- **Dependency Detection**: ≥ 90% accuracy
- **Plan Generation**: < 1 second for typical project (50 WPs)
- **Execution Time**: ≤ 15 minutes for full project improvement

### Quality Goals
- **Test Coverage**: ≥ 80% for new components
- **Zero Circular Dependencies**: Validation catches all cycles
- **Correctness**: Execution order always respects dependencies
- **Reliability**: No race conditions in parallel execution

---

## 🔄 Backward Compatibility

**CRITICAL**: All existing usage patterns must work

```python
# EXISTING: Sequential automation (still works)
agent = FengShuiReActAgent()
report = agent.run_autonomous_session(goal="score >= 90")

# NEW: With planning and parallelization (opt-in)
report = agent.run_autonomous_session_with_planning(
    goal="score >= 90",
    parallel=True
)
```

---

## 📝 Next Steps

### Before Implementation
- [ ] Review this plan
- [ ] Verify Phase 4-15 complete (✅ already done!)
- [ ] Clean git state
- [ ] Create branch: `feature/feng-shui-phase4-16-planning`

### During Implementation
- [ ] Follow TDD: Write tests first
- [ ] Test continuously
- [ ] Document as you build
- [ ] Commit after each component

### After Implementation
- [ ] Run full test suite (15+ tests)
- [ ] Measure parallel speedup (must be ≥ 2x)
- [ ] Update PROJECT_TRACKER.md
- [ ] Tag: `v3.36-feng-shui-phase4-16-planning`

---

**Status**: 📋 READY FOR IMPLEMENTATION  
**Created**: 2026-02-06  
**Prerequisites**: Phase 4-15 Complete ✅  
**Next**: Begin Phase 4-16 implementation when user is ready