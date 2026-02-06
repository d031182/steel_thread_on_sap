"""
Unit tests for Feng Shui State Analyzer

Tests architecture state analysis and scoring.
"""

import pytest
from pathlib import Path
from tools.fengshui.state_analyzer import (
    ArchitectureStateAnalyzer,
    ArchitectureState,
    ViolationInfo
)


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectureState:
    """Test suite for ArchitectureState dataclass"""
    
    def test_get_critical_violations(self):
        """Test retrieving CRITICAL severity violations"""
        # ARRANGE
        critical_v1 = ViolationInfo('structure', 'CRITICAL', 'module1/file.py', 10, 'Missing required', 'structure')
        critical_v2 = ViolationInfo('blueprint', 'CRITICAL', 'module2/api.py', 20, 'Not exported', 'blueprint')
        high_v1 = ViolationInfo('di_compliance', 'HIGH', 'module3/service.py', 30, 'Violation', 'di_compliance')
        
        state = ArchitectureState(
            feng_shui_score=60.0,
            violations_by_severity={
                'CRITICAL': [critical_v1, critical_v2],
                'HIGH': [high_v1]
            }
        )
        
        # ACT
        critical = state.get_critical_violations()
        
        # ASSERT
        assert len(critical) == 2
        assert all(v.severity == 'CRITICAL' for v in critical)
    
    def test_get_violations_for_module(self):
        """Test retrieving violations for specific module"""
        # ARRANGE
        v1 = ViolationInfo('structure', 'CRITICAL', 'module1/backend/api.py', 10, 'Issue', 'structure')
        v2 = ViolationInfo('blueprint', 'HIGH', 'module2/backend/service.py', 20, 'Issue', 'blueprint')
        v3 = ViolationInfo('di_compliance', 'MEDIUM', 'module1/tests/test.py', 30, 'Issue', 'di_compliance')
        
        state = ArchitectureState(
            feng_shui_score=70.0,
            violations_by_type={'structure': [v1], 'blueprint': [v2], 'di_compliance': [v3]}
        )
        
        # ACT
        module1_violations = state.get_violations_for_module('module1')
        
        # ASSERT
        assert len(module1_violations) == 2
        assert all('module1' in v.file_path for v in module1_violations)


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectureStateAnalyzer:
    """Test suite for ArchitectureStateAnalyzer"""
    
    def test_initialization(self):
        """Test analyzer initializes with correct defaults"""
        # ARRANGE & ACT
        analyzer = ArchitectureStateAnalyzer()
        
        # ASSERT
        assert analyzer.modules_dir == Path('modules')
        assert analyzer.quality_gate is None  # Lazy loaded
    
    def test_initialization_with_custom_path(self):
        """Test analyzer accepts custom modules directory"""
        # ARRANGE
        custom_path = Path('custom/modules')
        
        # ACT
        analyzer = ArchitectureStateAnalyzer(modules_dir=custom_path)
        
        # ASSERT
        assert analyzer.modules_dir == custom_path
    
    def test_calculate_feng_shui_score_perfect(self):
        """Test score calculation with no violations"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        violations_by_severity = {}
        
        # ACT
        score = analyzer.calculate_feng_shui_score(violations_by_severity)
        
        # ASSERT
        assert score == 100.0
    
    def test_calculate_feng_shui_score_with_critical(self):
        """Test score calculation with CRITICAL violations"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        violations_by_severity = {
            'CRITICAL': [
                ViolationInfo('type1', 'CRITICAL', 'file1', 10, 'desc', 'cat'),
                ViolationInfo('type2', 'CRITICAL', 'file2', 20, 'desc', 'cat')
            ]
        }
        
        # ACT
        score = analyzer.calculate_feng_shui_score(violations_by_severity)
        
        # ASSERT
        # 100 - (2 * 20) = 60
        assert score == 60.0
    
    def test_calculate_feng_shui_score_mixed_severity(self):
        """Test score calculation with mixed severities"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        violations_by_severity = {
            'CRITICAL': [ViolationInfo('t1', 'CRITICAL', 'f1', 1, 'd', 'c')],  # -20
            'HIGH': [ViolationInfo('t2', 'HIGH', 'f2', 2, 'd', 'c')],          # -10
            'MEDIUM': [ViolationInfo('t3', 'MEDIUM', 'f3', 3, 'd', 'c')],      # -5
            'LOW': [ViolationInfo('t4', 'LOW', 'f4', 4, 'd', 'c')]             # -2
        }
        
        # ACT
        score = analyzer.calculate_feng_shui_score(violations_by_severity)
        
        # ASSERT
        # 100 - 20 - 10 - 5 - 2 = 63
        assert score == 63.0
    
    def test_calculate_feng_shui_score_floor_at_zero(self):
        """Test score never goes below zero"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        # 10 CRITICAL violations = -200 points
        violations_by_severity = {
            'CRITICAL': [ViolationInfo('t', 'CRITICAL', 'f', 1, 'd', 'c') for _ in range(10)]
        }
        
        # ACT
        score = analyzer.calculate_feng_shui_score(violations_by_severity)
        
        # ASSERT
        assert score == 0.0
    
    def test_categorize_violations_by_type(self):
        """Test violations are grouped by type correctly"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        raw_violations = [
            {'type': 'structure', 'severity': 'CRITICAL', 'file_path': 'f1', 'line_number': 10, 'description': 'd1', 'category': 'structure'},
            {'type': 'structure', 'severity': 'HIGH', 'file_path': 'f2', 'line_number': 20, 'description': 'd2', 'category': 'structure'},
            {'type': 'blueprint', 'severity': 'MEDIUM', 'file_path': 'f3', 'line_number': 30, 'description': 'd3', 'category': 'blueprint'}
        ]
        
        # ACT
        categorized = analyzer.categorize_violations(raw_violations)
        
        # ASSERT
        assert 'structure' in categorized
        assert 'blueprint' in categorized
        assert len(categorized['structure']) == 2
        assert len(categorized['blueprint']) == 1
    
    def test_identify_critical_path_priority_order(self):
        """Test critical path identifies highest priority violations first"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        violations = {
            'type1': [ViolationInfo('type1', 'LOW', 'f1', 1, 'd', 'c')],
            'type2': [ViolationInfo('type2', 'CRITICAL', 'f2', 2, 'd', 'c')],
            'type3': [ViolationInfo('type3', 'MEDIUM', 'f3', 3, 'd', 'c')],
            'type4': [ViolationInfo('type4', 'HIGH', 'f4', 4, 'd', 'c')]
        }
        
        # ACT
        critical_path = analyzer.identify_critical_path(violations)
        
        # ASSERT
        assert critical_path[0] == 'type2'  # CRITICAL first
        assert critical_path[1] == 'type4'  # HIGH second
        assert critical_path[2] == 'type3'  # MEDIUM third
        assert critical_path[3] == 'type1'  # LOW last
    
    def test_identify_critical_path_deduplicates_types(self):
        """Test critical path doesn't include duplicate types"""
        # ARRANGE
        analyzer = ArchitectureStateAnalyzer()
        violations = {
            'type1': [
                ViolationInfo('type1', 'CRITICAL', 'f1', 1, 'd', 'c'),
                ViolationInfo('type1', 'HIGH', 'f2', 2, 'd', 'c')
            ]
        }
        
        # ACT
        critical_path = analyzer.identify_critical_path(violations)
        
        # ASSERT
        assert len(critical_path) == 1
        assert critical_path[0] == 'type1'


@pytest.mark.unit
@pytest.mark.fast
class TestViolationInfo:
    """Test suite for ViolationInfo dataclass"""
    
    def test_violation_info_creation(self):
        """Test ViolationInfo can be created with all fields"""
        # ARRANGE & ACT
        violation = ViolationInfo(
            type='structure',
            severity='CRITICAL',
            file_path='module1/backend/api.py',
            line_number=42,
            description='Missing required file',
            category='structure'
        )
        
        # ASSERT
        assert violation.type == 'structure'
        assert violation.severity == 'CRITICAL'
        assert violation.file_path == 'module1/backend/api.py'
        assert violation.line_number == 42
        assert violation.description == 'Missing required file'
        assert violation.category == 'structure'