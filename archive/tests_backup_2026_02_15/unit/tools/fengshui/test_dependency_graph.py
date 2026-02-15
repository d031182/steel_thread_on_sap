"""
Unit tests for DependencyGraph

Tests dependency detection, topological sorting, parallel groups, and critical path.
Part of Feng Shui Phase 4-16: Planning with Dependencies.
"""

import pytest
from tools.fengshui.dependency_graph import DependencyGraph, DependencyType
from tools.fengshui.execution_plan import WorkPackageNode


@pytest.mark.unit
@pytest.mark.fast
def test_add_work_package():
    """Test adding work package to graph"""
    # ARRANGE
    graph = DependencyGraph()
    wp = WorkPackageNode('WP-001', 'Test WP', 'Test description', 1.0)
    
    # ACT
    graph.add_work_package(wp)
    
    # ASSERT
    assert 'WP-001' in graph.nodes
    assert graph.nodes['WP-001'] == wp
    assert 'WP-001' in graph.edges


@pytest.mark.unit
@pytest.mark.fast
def test_add_dependency():
    """Test adding dependency between work packages"""
    # ARRANGE
    graph = DependencyGraph()
    wp1 = WorkPackageNode('WP-001', 'Foundation', 'Base work', 1.0)
    wp2 = WorkPackageNode('WP-002', 'Feature', 'Depends on foundation', 0.5)
    
    graph.add_work_package(wp1)
    graph.add_work_package(wp2)
    
    # ACT
    graph.add_dependency('WP-002', 'WP-001')  # WP-002 depends on WP-001
    
    # ASSERT
    assert 'WP-001' in graph.edges['WP-002']
    assert 'WP-001' in wp2.dependencies
    assert 'WP-002' in wp1.dependents


@pytest.mark.unit
def test_topological_sort_simple():
    """Test topological sorting respects dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    wp1 = WorkPackageNode('WP-001', 'Foundation', 'Base work', 1.0)
    wp2 = WorkPackageNode('WP-002', 'Feature', 'Depends on foundation', 0.5)
    
    graph.add_work_package(wp1)
    graph.add_work_package(wp2)
    graph.add_dependency('WP-002', 'WP-001')
    
    # ACT
    order = graph.topological_sort()
    
    # ASSERT
    assert len(order) == 2
    assert order.index('WP-001') < order.index('WP-002')


@pytest.mark.unit
def test_topological_sort_complex():
    """Test topological sort with complex dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    
    # Create diamond dependency structure:
    # WP-001 → WP-002 → WP-004
    #       ↘ WP-003 ↗
    wps = [
        WorkPackageNode('WP-001', 'Root', 'Root task', 1.0),
        WorkPackageNode('WP-002', 'Branch A', 'Depends on root', 0.5),
        WorkPackageNode('WP-003', 'Branch B', 'Depends on root', 0.5),
        WorkPackageNode('WP-004', 'Merge', 'Depends on both branches', 1.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    graph.add_dependency('WP-002', 'WP-001')
    graph.add_dependency('WP-003', 'WP-001')
    graph.add_dependency('WP-004', 'WP-002')
    graph.add_dependency('WP-004', 'WP-003')
    
    # ACT
    order = graph.topological_sort()
    
    # ASSERT
    assert len(order) == 4
    assert order[0] == 'WP-001'  # Root must be first
    assert order[3] == 'WP-004'  # Merge must be last
    # WP-002 and WP-003 can be in any order (both depend only on WP-001)
    assert set(order[1:3]) == {'WP-002', 'WP-003'}


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


@pytest.mark.unit
def test_detect_dependencies_interface_to_implementation():
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
def test_detect_dependencies_module_json_to_blueprint():
    """Test auto-detection of module.json → blueprint dependency"""
    # ARRANGE
    graph = DependencyGraph()
    module_wp = WorkPackageNode('WP-001', 'Module Config', 'Create module.json file', 0.5)
    blueprint_wp = WorkPackageNode('WP-002', 'Blueprint Setup', 'Configure blueprint registration', 1.0)
    
    graph.add_work_package(module_wp)
    graph.add_work_package(blueprint_wp)
    
    # ACT
    detected = graph.detect_dependencies()
    
    # ASSERT
    assert 'WP-002' in detected
    assert 'WP-001' in detected['WP-002']


@pytest.mark.unit
def test_detect_dependencies_test_to_coverage():
    """Test auto-detection of test → coverage validation dependency"""
    # ARRANGE
    graph = DependencyGraph()
    test_wp = WorkPackageNode('WP-001', 'Unit Tests', 'Write unit tests for module', 2.0)
    coverage_wp = WorkPackageNode('WP-002', 'Coverage Check', 'Validate test coverage meets 80%', 0.5)
    
    graph.add_work_package(test_wp)
    graph.add_work_package(coverage_wp)
    
    # ACT
    detected = graph.detect_dependencies()
    
    # ASSERT
    assert 'WP-002' in detected
    assert 'WP-001' in detected['WP-002']


@pytest.mark.unit
def test_find_parallel_groups_independent():
    """Test parallel group identification for independent WPs"""
    # ARRANGE
    graph = DependencyGraph()
    wps = [
        WorkPackageNode('WP-001', 'Task 1', 'Independent task 1', 1.0),
        WorkPackageNode('WP-002', 'Task 2', 'Independent task 2', 1.0),
        WorkPackageNode('WP-003', 'Task 3', 'Independent task 3', 1.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    # ACT
    groups = graph.find_parallel_groups()
    
    # ASSERT
    assert len(groups) == 1  # All can run in parallel
    assert len(groups[0]) == 3  # All 3 WPs in same group


@pytest.mark.unit
def test_find_parallel_groups_with_dependencies():
    """Test parallel groups respect dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    
    # WP-001 → WP-002, WP-003 (parallel) → WP-004
    wps = [
        WorkPackageNode('WP-001', 'Foundation', 'Base', 1.0),
        WorkPackageNode('WP-002', 'Feature A', 'Depends on foundation', 0.5),
        WorkPackageNode('WP-003', 'Feature B', 'Depends on foundation', 0.5),
        WorkPackageNode('WP-004', 'Integration', 'Depends on both features', 1.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    graph.add_dependency('WP-002', 'WP-001')
    graph.add_dependency('WP-003', 'WP-001')
    graph.add_dependency('WP-004', 'WP-002')
    graph.add_dependency('WP-004', 'WP-003')
    
    # ACT
    groups = graph.find_parallel_groups()
    
    # ASSERT
    assert len(groups) == 3
    assert groups[0] == ['WP-001']  # Foundation first
    assert set(groups[1]) == {'WP-002', 'WP-003'}  # Features in parallel
    assert groups[2] == ['WP-004']  # Integration last


@pytest.mark.unit
def test_calculate_critical_path():
    """Test critical path calculation"""
    # ARRANGE
    graph = DependencyGraph()
    
    # Create paths:
    # Path 1: WP-001 (1h) → WP-002 (0.5h) = 1.5h
    # Path 2: WP-001 (1h) → WP-003 (2h) = 3h ← Critical
    wps = [
        WorkPackageNode('WP-001', 'Root', 'Root', 1.0),
        WorkPackageNode('WP-002', 'Short', 'Short branch', 0.5),
        WorkPackageNode('WP-003', 'Long', 'Long branch', 2.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    graph.add_dependency('WP-002', 'WP-001')
    graph.add_dependency('WP-003', 'WP-001')
    
    # ACT
    path, time = graph.calculate_critical_path()
    
    # ASSERT
    assert 'WP-001' in path
    assert 'WP-003' in path
    assert time == 3.0  # 1h + 2h


@pytest.mark.unit
def test_validate_dependencies_missing_wp():
    """Test validation detects missing work packages"""
    # ARRANGE
    graph = DependencyGraph()
    wp = WorkPackageNode('WP-001', 'Task', 'Task with invalid dependency', 1.0)
    
    graph.add_work_package(wp)
    graph.add_dependency('WP-001', 'WP-999')  # Non-existent WP
    
    # ACT
    errors = graph.validate_dependencies()
    
    # ASSERT
    assert len(errors) > 0
    assert any('WP-999' in err for err in errors)


@pytest.mark.unit
def test_get_independent_work_packages():
    """Test identifying WPs with no dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    
    wps = [
        WorkPackageNode('WP-001', 'Independent 1', 'No deps', 1.0),
        WorkPackageNode('WP-002', 'Independent 2', 'No deps', 1.0),
        WorkPackageNode('WP-003', 'Dependent', 'Has deps', 1.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    graph.add_dependency('WP-003', 'WP-001')
    
    # ACT
    independent = graph.get_independent_work_packages()
    
    # ASSERT
    assert set(independent) == {'WP-001', 'WP-002'}


@pytest.mark.unit
def test_get_dependency_depth():
    """Test dependency depth calculation"""
    # ARRANGE
    graph = DependencyGraph()
    
    # Chain: WP-001 → WP-002 → WP-003
    wps = [
        WorkPackageNode('WP-001', 'Level 0', 'No deps', 1.0),
        WorkPackageNode('WP-002', 'Level 1', 'Depth 1', 1.0),
        WorkPackageNode('WP-003', 'Level 2', 'Depth 2', 1.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    graph.add_dependency('WP-002', 'WP-001')
    graph.add_dependency('WP-003', 'WP-002')
    
    # ACT
    depth_001 = graph.get_dependency_depth('WP-001')
    depth_002 = graph.get_dependency_depth('WP-002')
    depth_003 = graph.get_dependency_depth('WP-003')
    
    # ASSERT
    assert depth_001 == 0
    assert depth_002 == 1
    assert depth_003 == 2


@pytest.mark.unit
def test_get_dependency_tree():
    """Test dependency tree generation"""
    # ARRANGE
    graph = DependencyGraph()
    
    wps = [
        WorkPackageNode('WP-001', 'Root', 'Root', 1.0),
        WorkPackageNode('WP-002', 'Child', 'Child', 1.0)
    ]
    
    for wp in wps:
        graph.add_work_package(wp)
    
    graph.add_dependency('WP-002', 'WP-001')
    
    # ACT
    tree = graph.get_dependency_tree('WP-002')
    
    # ASSERT
    assert tree['wp_id'] == 'WP-002'
    assert len(tree['dependencies']) == 1
    assert tree['dependencies'][0]['wp_id'] == 'WP-001'


@pytest.mark.unit
def test_detect_dependencies_schema_to_migration():
    """Test auto-detection of schema → migration dependency"""
    # ARRANGE
    graph = DependencyGraph()
    schema_wp = WorkPackageNode('WP-001', 'Schema Update', 'Update database schema definition', 1.0)
    migration_wp = WorkPackageNode('WP-002', 'Data Migration', 'Migrate data after schema changes', 2.0)
    
    graph.add_work_package(schema_wp)
    graph.add_work_package(migration_wp)
    
    # ACT
    detected = graph.detect_dependencies()
    
    # ASSERT
    assert 'WP-002' in detected
    assert 'WP-001' in detected['WP-002']


@pytest.mark.unit
def test_detect_dependencies_file_ops_to_imports():
    """Test auto-detection of file operations → import updates dependency"""
    # ARRANGE
    graph = DependencyGraph()
    move_wp = WorkPackageNode('WP-001', 'File Move', 'Move files to new structure', 0.5)
    import_wp = WorkPackageNode('WP-002', 'Update Imports', 'Update import statements', 1.0)
    
    graph.add_work_package(move_wp)
    graph.add_work_package(import_wp)
    
    # ACT
    detected = graph.detect_dependencies()
    
    # ASSERT
    assert 'WP-002' in detected
    assert 'WP-001' in detected['WP-002']


@pytest.mark.unit
def test_topological_sort_with_priority():
    """Test topological sort respects priority when no dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    
    wp1 = WorkPackageNode('WP-001', 'Low Priority', 'Low', 1.0, priority=1)
    wp2 = WorkPackageNode('WP-002', 'High Priority', 'High', 1.0, priority=10)
    wp3 = WorkPackageNode('WP-003', 'Medium Priority', 'Medium', 1.0, priority=5)
    
    graph.add_work_package(wp1)
    graph.add_work_package(wp2)
    graph.add_work_package(wp3)
    
    # ACT
    order = graph.topological_sort()
    
    # ASSERT
    # Should be sorted by priority when no dependencies
    assert order[0] == 'WP-002'  # Highest priority first
    assert order[1] == 'WP-003'
    assert order[2] == 'WP-001'


@pytest.mark.unit
def test_validate_dependencies_orphaned():
    """Test validation detects orphaned dependencies"""
    # ARRANGE
    graph = DependencyGraph()
    wp = WorkPackageNode('WP-001', 'Task', 'Task', 1.0)
    wp.dependencies.add('WP-999')  # Orphaned dependency
    
    graph.add_work_package(wp)
    
    # ACT
    errors = graph.validate_dependencies()
    
    # ASSERT
    assert len(errors) > 0
    assert any('orphaned' in err.lower() or 'non-existent' in err.lower() for err in errors)


@pytest.mark.unit
def test_no_dependencies_all_parallel():
    """Test WPs with no dependencies form single parallel group"""
    # ARRANGE
    graph = DependencyGraph()
    
    for i in range(5):
        wp = WorkPackageNode(f'WP-{i:03d}', f'Task {i}', f'Independent task {i}', 0.5)
        graph.add_work_package(wp)
    
    # ACT
    groups = graph.find_parallel_groups()
    
    # ASSERT
    assert len(groups) == 1
    assert len(groups[0]) == 5