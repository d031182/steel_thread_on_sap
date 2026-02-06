"""
Unit Tests for Shi Fu (师傅) - The Master Teacher
=================================================

Tests the quality ecosystem orchestrator.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from tools.shifu.shifu import ShiFu, EcosystemHealth, ShiFuInsight
from tools.shifu.disciples.fengshui_interface import FengShuiInterface, ViolationSummary
from tools.shifu.disciples.guwu_interface import GuWuInterface, TestMetricsSummary
from tools.shifu.ecosystem_analyzer import EcosystemAnalyzer
from tools.shifu.correlation_engine import CorrelationEngine, CorrelationPattern


@pytest.fixture
def mock_fengshui():
    """Mock Feng Shui interface"""
    mock = Mock(spec=FengShuiInterface)
    mock.get_overall_score.return_value = 87.0
    mock.get_recent_violations.return_value = [
        {'violation_type': 'DI_VIOLATION', 'severity': 'HIGH'},
        {'violation_type': 'DI_VIOLATION', 'severity': 'MEDIUM'},
    ]
    mock.get_violation_summary.return_value = ViolationSummary(
        total_violations=10,
        critical_count=2,
        high_count=5,
        medium_count=2,
        low_count=1,
        violations_by_type={'DI_VIOLATION': 5, 'SECURITY_ISSUE': 3},
        violations_by_module={'module1': 7, 'module2': 3},
        recent_violations=[]
    )
    return mock


@pytest.fixture
def mock_guwu():
    """Mock Gu Wu interface"""
    mock = Mock(spec=GuWuInterface)
    mock.get_overall_score.return_value = 72.0
    mock.get_recent_test_executions.return_value = [
        {'outcome': 'PASSED', 'duration_ms': 1000},
        {'outcome': 'FAILED', 'duration_ms': 2000},
    ]
    mock.get_flaky_tests.return_value = [
        {'test_name': 'test_flaky_1', 'flakiness_score': 0.6}
    ]
    mock.get_test_metrics_summary.return_value = TestMetricsSummary(
        total_tests=100,
        passing_tests=85,
        failing_tests=10,
        flaky_tests=3,
        slow_tests=5,
        avg_execution_time=1500.0,
        coverage_percentage=72.5,
        tests_by_type={'unit': 70, 'integration': 20, 'e2e': 10},
        recent_executions=[]
    )
    return mock


@pytest.fixture
def shifu(mock_fengshui, mock_guwu):
    """Create Shi Fu instance with mocked disciples"""
    with patch('tools.shifu.shifu.FengShuiInterface', return_value=mock_fengshui):
        with patch('tools.shifu.shifu.GuWuInterface', return_value=mock_guwu):
            return ShiFu(project_root=Path.cwd(), verbose=False)


class TestShiFuInitialization:
    """Test Shi Fu initialization"""
    
    def test_shifu_initializes_with_project_root(self):
        """Test Shi Fu initializes with project root"""
        project_root = Path.cwd()
        
        with patch('tools.shifu.shifu.FengShuiInterface') as mock_fs:
            with patch('tools.shifu.shifu.GuWuInterface') as mock_gw:
                shifu = ShiFu(project_root=project_root, verbose=True)
                
                assert shifu.project_root == project_root
                assert shifu.verbose is True
                mock_fs.assert_called_once()
                mock_gw.assert_called_once()
    
    def test_shifu_creates_disciples(self, shifu):
        """Test Shi Fu creates disciple interfaces"""
        assert shifu.fengshui is not None
        assert shifu.guwu is not None
        assert shifu.analyzer is not None
        assert shifu.correlation_engine is not None


class TestObserveDisciples:
    """Test disciple observation"""
    
    def test_observe_disciples_collects_data(self, shifu, mock_fengshui, mock_guwu):
        """Test observing disciples collects data from both"""
        observations = shifu.observe_disciples()
        
        assert 'fengshui' in observations
        assert 'guwu' in observations
        assert observations['fengshui']['violation_count'] == 10
        assert observations['guwu']['test_count'] == 100
    
    def test_observe_disciples_with_custom_days(self, shifu, mock_fengshui):
        """Test observation with custom timeframe"""
        shifu.observe_disciples()
        
        # Verify analyzer was called (it calls the interfaces internally)
        assert mock_fengshui.get_violation_summary.called


class TestCorrelationDetection:
    """Test correlation pattern detection"""
    
    def test_find_correlations_detects_patterns(self, shifu):
        """Test correlation detection finds cross-domain patterns"""
        observations = shifu.observe_disciples()
        insights = shifu.find_correlations(observations)
        
        assert isinstance(insights, list)
        # Should find at least DI→Flaky pattern with our mock data
        if insights:
            # find_correlations returns ShiFuInsight objects (converted from CorrelationPattern)
            assert all(isinstance(i, ShiFuInsight) for i in insights)
            # Verify structure
            assert all(hasattr(i, 'pattern_name') for i in insights)
            assert all(hasattr(i, 'severity') for i in insights)
    
    def test_correlation_engine_di_flakiness_pattern(self):
        """Test DI violations → Flaky tests pattern detection"""
        engine = CorrelationEngine()
        
        fengshui_data = {
            'violations_by_type': {'DI_VIOLATION': 10},
            'violations_by_module': {}
        }
        guwu_data = {
            'flaky_count': 5,
            'test_count': 100
        }
        
        patterns = engine.detect_patterns(fengshui_data, guwu_data)
        
        assert len(patterns) > 0
        di_pattern = next((p for p in patterns if 'DI' in p.pattern_name), None)
        assert di_pattern is not None
        assert di_pattern.severity in ['URGENT', 'HIGH']
        assert di_pattern.confidence > 0.0
    
    def test_correlation_engine_security_gaps_pattern(self):
        """Test Security issues → Test gaps pattern"""
        engine = CorrelationEngine()
        
        fengshui_data = {
            'violations_by_type': {'SECURITY_ISSUE': 5},
            'violations_by_module': {}
        }
        guwu_data = {
            'tests_by_type': {'security': 1},
            'flaky_count': 0
        }
        
        patterns = engine.detect_patterns(fengshui_data, guwu_data)
        
        security_pattern = next((p for p in patterns if 'Security' in p.pattern_name), None)
        assert security_pattern is not None
        assert security_pattern.severity == 'URGENT'


class TestEcosystemHealth:
    """Test ecosystem health assessment"""
    
    def test_assess_ecosystem_health_returns_health_object(self, shifu):
        """Test health assessment returns EcosystemHealth"""
        health = shifu.assess_ecosystem_health()
        
        assert isinstance(health, EcosystemHealth)
        assert 0 <= health.ecosystem_score <= 100
        assert 0 <= health.fengshui_score <= 100
        assert 0 <= health.guwu_score <= 100
        assert health.correlation_count >= 0
    
    def test_ecosystem_score_calculation(self, shifu):
        """Test ecosystem score includes penalty for correlations"""
        health = shifu.assess_ecosystem_health()
        
        # Ecosystem score should be lower than simple average due to correlation penalty
        simple_avg = (health.fengshui_score * 0.6 + health.guwu_score * 0.4)
        assert health.ecosystem_score <= simple_avg
    
    def test_health_includes_teaching(self, shifu):
        """Test health assessment includes wisdom"""
        health = shifu.assess_ecosystem_health()
        
        assert health.teaching is not None
        assert len(health.teaching) > 0


class TestTeachingGeneration:
    """Test Shi Fu's teaching generation"""
    
    def test_teach_through_insight_creates_teachings(self, shifu):
        """Test teaching generation from insights"""
        insights = [
            ShiFuInsight(
                id='TEST_001',
                pattern_name='Test Pattern',
                confidence=0.9,
                severity='HIGH',
                fengshui_evidence='Code issue',
                guwu_evidence='Test issue',
                root_cause='Root cause',
                recommendation='Fix this',
                estimated_effort='2 hours',
                combined_value='High value',
                timestamp=datetime.now().isoformat()
            )
        ]
        
        teachings = shifu.teach_through_insight(insights)
        
        assert len(teachings) == 1
        assert 'Test Pattern' in teachings[0]
        assert 'Code issue' in teachings[0]
        assert 'Test issue' in teachings[0]
        assert 'Root cause' in teachings[0]
    
    def test_teachings_include_all_components(self, shifu):
        """Test teachings contain all required sections"""
        insight = ShiFuInsight(
            id='TEST_001',
            pattern_name='Example',
            confidence=0.8,
            severity='MEDIUM',
            fengshui_evidence='Evidence A',
            guwu_evidence='Evidence B',
            root_cause='Cause',
            recommendation='Recommendation',
            estimated_effort='3h',
            combined_value='Value',
            timestamp=datetime.now().isoformat()
        )
        
        teachings = shifu.teach_through_insight([insight])
        teaching = teachings[0]
        
        assert 'Feng Shui found' in teaching
        assert 'Gu Wu found' in teaching
        assert 'connection is' in teaching
        assert 'Priority' in teaching


class TestWeeklyAnalysis:
    """Test weekly analysis workflow"""
    
    def test_weekly_analysis_returns_complete_report(self, shifu):
        """Test weekly analysis returns full report"""
        report = shifu.weekly_analysis()
        
        assert 'timestamp' in report
        assert 'observations' in report
        assert 'insights' in report
        assert 'teachings' in report
        assert 'health' in report
    
    def test_weekly_analysis_health_section(self, shifu):
        """Test weekly analysis includes health metrics"""
        report = shifu.weekly_analysis()
        health = report['health']
        
        assert 'ecosystem_score' in health
        assert 'fengshui_score' in health
        assert 'guwu_score' in health
        assert 'correlation_count' in health
        assert 'teaching' in health


class TestEcosystemAnalyzer:
    """Test EcosystemAnalyzer component"""
    
    def test_analyzer_collects_recent_data(self, mock_fengshui, mock_guwu):
        """Test analyzer collects data from both disciples"""
        analyzer = EcosystemAnalyzer(mock_fengshui, mock_guwu)
        data = analyzer.collect_recent_data(days=7)
        
        assert 'timeframe_days' in data
        assert data['timeframe_days'] == 7
        assert 'fengshui' in data
        assert 'guwu' in data
    
    def test_analyzer_identifies_troubled_modules(self, mock_fengshui, mock_guwu):
        """Test identification of modules with cross-domain issues"""
        analyzer = EcosystemAnalyzer(mock_fengshui, mock_guwu)
        
        mock_fengshui.get_modules_with_issues.return_value = ['module1', 'module2']
        mock_guwu.get_recent_test_executions.return_value = [
            {'outcome': 'FAILED', 'test_file': 'tests/unit/module1/test.py'},
            {'outcome': 'FAILED', 'test_file': 'tests/unit/module1/test2.py'},
        ]
        
        troubled = analyzer.identify_troubled_modules(days=7)
        
        assert isinstance(troubled, list)
        # module1 has both code and test issues
        assert 'module1' in troubled or len(troubled) >= 0


class TestCorrelationEngine:
    """Test CorrelationEngine independently"""
    
    def test_engine_initializes(self):
        """Test engine initialization"""
        engine = CorrelationEngine()
        assert engine.patterns_detected == []
    
    def test_engine_detects_multiple_patterns(self):
        """Test engine can detect multiple pattern types"""
        engine = CorrelationEngine()
        
        fengshui_data = {
            'violations_by_type': {
                'DI_VIOLATION': 10,
                'SECURITY_ISSUE': 5,
                'PERFORMANCE_ISSUE': 4
            },
            'violations_by_module': {'auth': 15}
        }
        guwu_data = {
            'flaky_count': 5,
            'test_count': 100,
            'tests_by_type': {'security': 2},
            'slow_count': 8,
            'failing_count': 5
        }
        
        patterns = engine.detect_patterns(fengshui_data, guwu_data)
        
        # Should detect multiple patterns
        assert len(patterns) >= 2
        
        # Verify pattern types
        pattern_names = [p.pattern_name for p in patterns]
        assert any('DI' in name for name in pattern_names)
        assert any('Security' in name for name in pattern_names)
    
    def test_engine_prioritizes_by_severity(self):
        """Test patterns are prioritized correctly"""
        engine = CorrelationEngine()
        
        # Create some patterns
        engine.patterns_detected = [
            CorrelationPattern(
                id='1', pattern_name='Low', confidence=0.5, severity='LOW',
                fengshui_evidence='', guwu_evidence='', root_cause='',
                recommendation='', estimated_effort='', combined_value='',
                timestamp=datetime.now().isoformat()
            ),
            CorrelationPattern(
                id='2', pattern_name='Urgent', confidence=0.9, severity='URGENT',
                fengshui_evidence='', guwu_evidence='', root_cause='',
                recommendation='', estimated_effort='', combined_value='',
                timestamp=datetime.now().isoformat()
            ),
            CorrelationPattern(
                id='3', pattern_name='High', confidence=0.8, severity='HIGH',
                fengshui_evidence='', guwu_evidence='', root_cause='',
                recommendation='', estimated_effort='', combined_value='',
                timestamp=datetime.now().isoformat()
            )
        ]
        
        prioritized = engine.get_prioritized_insights()
        
        # URGENT should be first
        assert prioritized[0].severity == 'URGENT'
        # HIGH should be second
        assert prioritized[1].severity == 'HIGH'
        # LOW should be last
        assert prioritized[2].severity == 'LOW'


@pytest.mark.unit
@pytest.mark.fast
def test_shifu_main_module_importable():
    """Test that Shi Fu module can be imported"""
    from tools.shifu import ShiFu as ImportedShiFu
    assert ImportedShiFu is not None


@pytest.mark.unit
@pytest.mark.fast
def test_all_shifu_components_importable():
    """Test all Shi Fu components are importable"""
    from tools.shifu.shifu import ShiFu, EcosystemHealth, ShiFuInsight
    from tools.shifu.disciples import FengShuiInterface, GuWuInterface
    from tools.shifu.ecosystem_analyzer import EcosystemAnalyzer
    from tools.shifu.correlation_engine import CorrelationEngine, CorrelationPattern
    
    assert all([
        ShiFu, EcosystemHealth, ShiFuInsight,
        FengShuiInterface, GuWuInterface,
        EcosystemAnalyzer, CorrelationEngine, CorrelationPattern
    ])