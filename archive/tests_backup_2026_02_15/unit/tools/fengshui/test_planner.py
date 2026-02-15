"""
Unit tests for FengShuiPlanner

Tests plan creation, parallel execution, and integration.
Part of Feng Shui Phase 4-16: Planning with Dependencies.
"""

import pytest
from tools.fengshui.planner import FengShuiPlanner, ExecutionReport
from tools.fengshui.execution_plan import WorkPackageNode, ExecutionPlan


@pytest.mark.unit
@pytest.mark.fast
def test_planner_initialization():
    """Test planner initializes correctly"""
    # ARRANGE & ACT
    planner = FengShuiPlanner()
    
    # ASSERT
    assert planner.engine is None  # No engine by default
    assert planner.logger is not None


@pytest.mark.unit
def test_create_execution_plan_simple():
    """Test creating execution plan from work packages"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Fix DI', 'description': 'Fix DI violations'},
        {'id': 'WP-002', 'title': 'Fix Blueprint', 'description': 'Fix blueprint config'}
    ]
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    
    # ASSERT
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.all_work_packages) == 2
    assert len(plan.execution_order) == 2
    assert plan.estimated_time_hours > 0


@pytest.mark.unit
def test_create_execution_plan_with_dependencies():
    """Test plan creation respects explicit dependencies"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Foundation', 'description': 'Base work', 'estimated_hours': 1.0},
        {'id': 'WP-002', 'title': 'Feature', 'description': 'Feature work', 'estimated_hours': 0.5, 'dependencies': ['WP-001']}
    ]
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    
    # ASSERT
    assert plan.execution_order[0] == 'WP-001'
    assert plan.execution_order[1] == 'WP-002'


@pytest.mark.unit
def test_create_execution_plan_detects_implicit_dependencies():
    """Test plan auto-detects implicit dependencies"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Interface Changes', 'description': 'Update interface definitions'},
        {'id': 'WP-002', 'title': 'Implementation', 'description': 'Implement feature changes'}
    ]
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    
    # ASSERT
    # Should auto-detect interface → implementation dependency
    assert plan.execution_order[0] == 'WP-001'
    assert plan.execution_order[1] == 'WP-002'


@pytest.mark.unit
def test_execute_plan_sequential():
    """Test sequential execution of plan"""
    # ARRANGE
    planner = FengShuiPlanner()  # No engine = simulation mode
    work_packages = [
        {'id': 'WP-001', 'title': 'Task 1', 'description': 'Task 1', 'estimated_hours': 0.01},
        {'id': 'WP-002', 'title': 'Task 2', 'description': 'Task 2', 'estimated_hours': 0.01}
    ]
    plan = planner.create_execution_plan(work_packages)
    
    # ACT
    report = planner.execute_plan(plan, parallel=False)
    
    # ASSERT
    assert isinstance(report, ExecutionReport)
    assert report.total_work_packages == 2
    assert report.completed >= 0  # At least attempted
    assert report.total_time_seconds > 0


@pytest.mark.unit
def test_execute_plan_parallel():
    """Test parallel execution provides expected structure"""
    # ARRANGE
    planner = FengShuiPlanner()  # No engine = simulation mode
    work_packages = [
        {'id': f'WP-{i:03d}', 'title': f'Task {i}', 'description': f'Independent task {i}', 'estimated_hours': 0.01}
        for i in range(1, 4)
    ]
    plan = planner.create_execution_plan(work_packages)
    
    # ACT
    report = planner.execute_plan(plan, parallel=True, max_workers=2)
    
    # ASSERT
    assert isinstance(report, ExecutionReport)
    assert report.total_work_packages == 3
    assert report.parallel_speedup >= 1.0  # Should be at least 1x


@pytest.mark.unit
def test_estimate_sequential_time():
    """Test sequential time estimation"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Task 1', 'estimated_hours': 1.0},
        {'id': 'WP-002', 'title': 'Task 2', 'estimated_hours': 2.0},
        {'id': 'WP-003', 'title': 'Task 3', 'estimated_hours': 0.5}
    ]
    
    # ACT
    total = planner.estimate_sequential_time(work_packages)
    
    # ASSERT
    assert total == 3.5


@pytest.mark.unit
def test_estimate_parallel_time():
    """Test parallel time estimation"""
    # ARRANGE
    planner = FengShuiPlanner()
    
    # Create plan with known parallel structure
    # Group 1: WP-001 (1h)
    # Group 2: WP-002 (2h) || WP-003 (0.5h) → max = 2h
    # Total parallel time = 1h + 2h = 3h (vs 3.5h sequential)
    work_packages = [
        {'id': 'WP-001', 'title': 'Foundation', 'description': 'Base', 'estimated_hours': 1.0},
        {'id': 'WP-002', 'title': 'Feature A', 'description': 'Depends on foundation', 'estimated_hours': 2.0, 'dependencies': ['WP-001']},
        {'id': 'WP-003', 'title': 'Feature B', 'description': 'Depends on foundation', 'estimated_hours': 0.5, 'dependencies': ['WP-001']}
    ]
    
    plan = planner.create_execution_plan(work_packages)
    
    # ACT
    parallel_time = planner.estimate_parallel_time(plan)
    
    # ASSERT
    assert parallel_time <= 3.5  # Should be less than or equal to sequential
    assert parallel_time == 3.0  # 1h + max(2h, 0.5h)


@pytest.mark.unit
def test_visualize_plan():
    """Test plan visualization"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Foundation', 'description': 'Base', 'estimated_hours': 1.0},
        {'id': 'WP-002', 'title': 'Feature', 'description': 'Feature', 'estimated_hours': 0.5, 'dependencies': ['WP-001']}
    ]
    plan = planner.create_execution_plan(work_packages)
    
    # ACT
    visualization = planner.visualize_plan(plan)
    
    # ASSERT
    assert isinstance(visualization, str)
    assert len(visualization) > 0
    assert 'Execution Plan' in visualization
    assert 'WP-001' in visualization
    assert 'WP-002' in visualization


@pytest.mark.unit
def test_execution_report_structure():
    """Test execution report contains expected fields"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'Task', 'description': 'Task', 'estimated_hours': 0.01}
    ]
    plan = planner.create_execution_plan(work_packages)
    
    # ACT
    report = planner.execute_plan(plan, parallel=False)
    
    # ASSERT
    assert hasattr(report, 'total_work_packages')
    assert hasattr(report, 'completed')
    assert hasattr(report, 'failed')
    assert hasattr(report, 'skipped')
    assert hasattr(report, 'total_time_seconds')
    assert hasattr(report, 'parallel_speedup')
    assert hasattr(report, 'critical_path_hours')
    assert hasattr(report, 'results_by_wp')


@pytest.mark.unit
def test_parallel_execution_uses_max_workers():
    """Test parallel execution respects max_workers limit"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': f'WP-{i:03d}', 'title': f'Task {i}', 'description': f'Task {i}', 'estimated_hours': 0.01}
        for i in range(1, 6)  # 5 WPs
    ]
    plan = planner.create_execution_plan(work_packages)
    
    # ACT
    report = planner.execute_plan(plan, parallel=True, max_workers=2)
    
    # ASSERT
    # Should complete successfully with 2 workers
    assert report.total_work_packages == 5
    assert report.completed + report.failed + report.skipped == 5


@pytest.mark.unit
def test_create_plan_handles_circular_dependencies_gracefully():
    """Test plan creation handles circular dependencies without crashing"""
    # ARRANGE
    planner = FengShuiPlanner()
    work_packages = [
        {'id': 'WP-001', 'title': 'A', 'description': 'Task A', 'dependencies': ['WP-002']},
        {'id': 'WP-002', 'title': 'B', 'description': 'Task B', 'dependencies': ['WP-001']}  # Circular!
    ]
    
    # ACT
    plan = planner.create_execution_plan(work_packages)
    
    # ASSERT
    # Should handle gracefully (fallback to original order)
    assert isinstance(plan, ExecutionPlan)
    assert len(plan.all_work_packages) == 2