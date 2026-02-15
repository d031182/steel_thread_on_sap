"""
Unit Tests for Gu Wu Strategy Pattern

Tests all concrete strategies (Flakiness, Performance, Coverage)
and the GuWuAnalyzer context class.
"""

import pytest
from datetime import datetime

from tools.guwu.strategies import (
    GuWuAnalyzer,
    FlakynessAnalysisStrategy,
    PerformanceAnalysisStrategy,
    CoverageAnalysisStrategy,
    AnalysisResult
)


class TestFlakynessAnalysisStrategy:
    """Test flakiness detection strategy"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_high_flakiness_detected(self):
        """Test detection of highly flaky test (score > 0.3)"""
        # ARRANGE
        strategy = FlakynessAnalysisStrategy(sensitivity=1.0)
        test_data = {
            'test_id': 'test_flaky_endpoint',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'failed'},
                {'outcome': 'passed'},
                {'outcome': 'failed'},
                {'outcome': 'passed'}
            ]
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['severity'] == 'high'
        assert result.data['score'] > 0.3
        assert result.data['transitions'] == 4
        assert result.confidence >= 0.8
        assert '⚠️ HIGH FLAKINESS' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_stable_test_low_flakiness(self):
        """Test stable test shows low flakiness (score <= 0.15)"""
        # ARRANGE
        strategy = FlakynessAnalysisStrategy(sensitivity=1.0)
        test_data = {
            'test_id': 'test_stable_endpoint',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'passed'},
                {'outcome': 'passed'},
                {'outcome': 'passed'},
                {'outcome': 'passed'}
            ]
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['severity'] == 'low'
        assert result.data['score'] == 0.0
        assert result.data['transitions'] == 0
        assert '✓ LOW FLAKINESS' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_insufficient_data_handling(self):
        """Test handling of insufficient test history"""
        # ARRANGE
        strategy = FlakynessAnalysisStrategy()
        test_data = {
            'test_id': 'test_new_endpoint',
            'history': [
                {'outcome': 'passed'}
            ]
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['severity'] == 'insufficient_data'
        assert result.confidence == 0.3
        assert 'Need at least 3 test runs' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_sensitivity_affects_score(self):
        """Test sensitivity parameter affects flakiness score"""
        # ARRANGE
        test_data = {
            'test_id': 'test_endpoint',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'failed'},
                {'outcome': 'passed'}
            ]
        }
        
        # ACT
        result_low_sens = FlakynessAnalysisStrategy(sensitivity=0.5).analyze(test_data)
        result_high_sens = FlakynessAnalysisStrategy(sensitivity=2.0).analyze(test_data)
        
        # ASSERT
        assert result_high_sens.data['score'] > result_low_sens.data['score']
        assert result_high_sens.data['score'] == result_low_sens.data['score'] * 4  # 2.0 / 0.5


class TestPerformanceAnalysisStrategy:
    """Test performance analysis strategy"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_critical_slow_test_detected(self):
        """Test detection of critically slow test (> 2x threshold)"""
        # ARRANGE
        strategy = PerformanceAnalysisStrategy(threshold=5.0)
        test_data = {
            'test_id': 'test_very_slow_endpoint',
            'durations': [12.0, 11.5, 13.0, 12.5]
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['severity'] == 'critical'
        assert result.data['avg_duration'] > 10.0
        assert result.data['slowdown_factor'] > 2.0
        assert result.confidence == 1.0
        assert '🔴 CRITICAL' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_fast_test_low_severity(self):
        """Test fast test shows low severity"""
        # ARRANGE
        strategy = PerformanceAnalysisStrategy(threshold=5.0)
        test_data = {
            'test_id': 'test_fast_endpoint',
            'durations': [0.5, 0.6, 0.4, 0.5]
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['severity'] == 'low'
        assert result.data['avg_duration'] < 1.0
        assert '✓ LOW' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_high_variance_warning(self):
        """Test warning for high duration variance"""
        # ARRANGE
        strategy = PerformanceAnalysisStrategy(threshold=5.0)
        test_data = {
            'test_id': 'test_inconsistent_endpoint',
            'durations': [1.0, 1.2, 8.0, 1.1]  # One outlier
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['max_duration'] > result.data['avg_duration'] * 1.5
        assert any('High variance detected' in rec for rec in result.recommendations)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_no_duration_data_handling(self):
        """Test handling of empty duration list"""
        # ARRANGE
        strategy = PerformanceAnalysisStrategy()
        test_data = {
            'test_id': 'test_no_data',
            'durations': []
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['severity'] == 'no_data'
        assert result.confidence == 0.0


class TestCoverageAnalysisStrategy:
    """Test coverage analysis strategy"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_critical_coverage_gap(self):
        """Test detection of critical coverage gap (< 50%)"""
        # ARRANGE
        strategy = CoverageAnalysisStrategy(target_coverage=70.0)
        test_data = {
            'test_id': 'module::poorly_tested',
            'coverage': {
                'lines_covered': 40,
                'total_lines': 100,
                'uncovered_lines': list(range(60, 100))
            }
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['coverage_pct'] == 40.0
        assert result.data['priority'] == 'critical'
        assert result.data['gap_lines'] == 60
        assert result.confidence == 1.0
        assert '🔴 CRITICAL' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_good_coverage_low_priority(self):
        """Test good coverage shows low priority (> 85%)"""
        # ARRANGE
        strategy = CoverageAnalysisStrategy(target_coverage=70.0)
        test_data = {
            'test_id': 'module::well_tested',
            'coverage': {
                'lines_covered': 90,
                'total_lines': 100,
                'uncovered_lines': list(range(90, 100))
            }
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['coverage_pct'] == 90.0
        assert result.data['priority'] == 'low'
        assert result.data['gap_lines'] == 10
        assert '✓ LOW' in result.recommendations[0]
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_coverage_deficit_calculation(self):
        """Test coverage deficit is calculated correctly"""
        # ARRANGE
        strategy = CoverageAnalysisStrategy(target_coverage=80.0)
        test_data = {
            'test_id': 'module::partially_tested',
            'coverage': {
                'lines_covered': 60,
                'total_lines': 100
            }
        }
        
        # ACT
        result = strategy.analyze(test_data)
        
        # ASSERT
        assert result.data['coverage_pct'] == 60.0
        assert result.data['coverage_deficit'] == 20.0  # 80 - 60


class TestGuWuAnalyzer:
    """Test the GuWuAnalyzer context class"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_single_strategy_analysis(self):
        """Test analysis with single strategy"""
        # ARRANGE
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        test_data = {
            'test_id': 'test_endpoint',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'failed'},
                {'outcome': 'passed'}
            ]
        }
        
        # ACT
        result = analyzer.analyze(test_data)
        
        # ASSERT
        assert isinstance(result, AnalysisResult)
        assert result.strategy == 'flakiness_transition_based'
        assert len(analyzer.get_strategy_history()) == 1
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_strategy_switching(self):
        """Test switching strategies at runtime"""
        # ARRANGE
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        
        # ACT
        analyzer.set_strategy(PerformanceAnalysisStrategy(threshold=3.0))
        
        # ASSERT
        assert analyzer.strategy.get_strategy_name() == 'performance_threshold_based'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_multiple_strategies_analysis(self):
        """Test running multiple strategies on same data"""
        # ARRANGE
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        test_data = {
            'test_id': 'test_endpoint',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'passed'},
                {'outcome': 'passed'}
            ],
            'durations': [2.0, 2.1, 1.9],
            'coverage': {
                'lines_covered': 80,
                'total_lines': 100
            }
        }
        
        strategies = [
            FlakynessAnalysisStrategy(),
            PerformanceAnalysisStrategy(threshold=5.0),
            CoverageAnalysisStrategy(target_coverage=70.0)
        ]
        
        # ACT
        results = analyzer.analyze_with_multiple_strategies(test_data, strategies)
        
        # ASSERT
        assert len(results) == 3
        assert results[0].strategy == 'flakiness_transition_based'
        assert results[1].strategy == 'performance_threshold_based'
        assert results[2].strategy == 'coverage_gap_analysis'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_strategy_history_tracking(self):
        """Test strategy usage is tracked"""
        # ARRANGE
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        test_data = {
            'test_id': 'test_1',
            'history': [{'outcome': 'passed'}, {'outcome': 'passed'}, {'outcome': 'passed'}]
        }
        
        # ACT
        analyzer.analyze(test_data)
        analyzer.set_strategy(PerformanceAnalysisStrategy())
        test_data['durations'] = [1.0]
        analyzer.analyze(test_data)
        
        history = analyzer.get_strategy_history()
        
        # ASSERT
        assert len(history) == 2
        assert history[0]['strategy'] == 'flakiness_transition_based'
        assert history[1]['strategy'] == 'performance_threshold_based'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_history_clearing(self):
        """Test history can be cleared"""
        # ARRANGE
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        test_data = {
            'test_id': 'test_1',
            'history': [{'outcome': 'passed'}, {'outcome': 'passed'}, {'outcome': 'passed'}]
        }
        analyzer.analyze(test_data)
        
        # ACT
        analyzer.clear_history()
        
        # ASSERT
        assert len(analyzer.get_strategy_history()) == 0


class TestStrategyValidation:
    """Test strategy validation and error handling"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_missing_required_keys_raises_error(self):
        """Test that missing required keys raises ValueError"""
        # ARRANGE
        strategy = FlakynessAnalysisStrategy()
        test_data = {
            'test_id': 'test_endpoint'
            # Missing 'history' key
        }
        
        # ACT & ASSERT
        with pytest.raises(ValueError) as exc_info:
            strategy.analyze(test_data)
        
        assert 'missing required keys' in str(exc_info.value).lower()
        assert 'history' in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_analysis_result_to_dict(self):
        """Test AnalysisResult can be serialized"""
        # ARRANGE
        result = AnalysisResult(
            strategy='test_strategy',
            timestamp=datetime.now(),
            data={'key': 'value'},
            confidence=0.9,
            recommendations=['Action 1']
        )
        
        # ACT
        result_dict = result.to_dict()
        
        # ASSERT
        assert result_dict['strategy'] == 'test_strategy'
        assert 'timestamp' in result_dict
        assert result_dict['data'] == {'key': 'value'}
        assert result_dict['confidence'] == 0.9
        assert result_dict['recommendations'] == ['Action 1']


class TestStrategyIntegration:
    """Integration tests for strategy pattern"""
    
    @pytest.mark.integration
    def test_real_world_multi_strategy_analysis(self):
        """Test realistic scenario with all three strategies"""
        # ARRANGE
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        
        # Realistic test data
        test_data = {
            'test_id': 'tests/unit/modules/knowledge_graph/test_api.py::test_get_graph',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'passed'},
                {'outcome': 'failed'},  # One failure
                {'outcome': 'passed'},
                {'outcome': 'passed'}
            ],
            'durations': [3.2, 3.5, 3.1, 3.4, 3.3],
            'coverage': {
                'lines_covered': 85,
                'total_lines': 120,
                'uncovered_lines': list(range(85, 120))
            }
        }
        
        strategies = [
            FlakynessAnalysisStrategy(sensitivity=1.0),
            PerformanceAnalysisStrategy(threshold=5.0),
            CoverageAnalysisStrategy(target_coverage=70.0)
        ]
        
        # ACT
        results = analyzer.analyze_with_multiple_strategies(test_data, strategies)
        
        # ASSERT
        assert len(results) == 3
        
        # Flakiness: High (2 transitions in 5 runs = 40% transition rate)
        assert results[0].data['severity'] == 'high'
        assert results[0].data['transitions'] == 2
        
        # Performance: Low (avg ~3.3s < 5.0s threshold)
        assert results[1].data['severity'] == 'low'
        assert results[1].data['avg_duration'] < 5.0
        
        # Coverage: Medium/Low (85/120 = 70.8%)
        assert results[2].data['coverage_pct'] > 70.0
        assert results[2].data['priority'] in ['medium', 'low']