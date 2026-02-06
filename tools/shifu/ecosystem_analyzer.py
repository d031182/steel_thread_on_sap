"""
Ecosystem Analyzer: Unified Data Collector for Shi Fu
=====================================================

Collects and harmonizes data from both Feng Shui and Gu Wu disciples.
"""

import logging
from typing import Dict, List
from pathlib import Path

from .disciples.fengshui_interface import FengShuiInterface
from .disciples.guwu_interface import GuWuInterface


logger = logging.getLogger(__name__)


class EcosystemAnalyzer:
    """
    Unified data collector for quality ecosystem
    
    Orchestrates data collection from both disciples and provides
    harmonized views of the quality landscape.
    """
    
    def __init__(
        self,
        fengshui: FengShuiInterface,
        guwu: GuWuInterface
    ):
        """
        Initialize ecosystem analyzer
        
        Args:
            fengshui: Feng Shui interface instance
            guwu: Gu Wu interface instance
        """
        self.fengshui = fengshui
        self.guwu = guwu
    
    def collect_recent_data(self, days: int = 7) -> Dict:
        """
        Collect recent data from both disciples
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dictionary with harmonized data from both systems
        """
        logger.info(f"[Ecosystem Analyzer] Collecting data from last {days} days...")
        
        # Collect from Feng Shui (code quality)
        fengshui_violations = self.fengshui.get_recent_violations(days)
        fengshui_summary = self.fengshui.get_violation_summary(days)
        fengshui_score = self.fengshui.get_overall_score()
        
        # Collect from Gu Wu (test quality)
        guwu_executions = self.guwu.get_recent_test_executions(days)
        guwu_flaky = self.guwu.get_flaky_tests(days)
        guwu_summary = self.guwu.get_test_metrics_summary(days)
        guwu_score = self.guwu.get_overall_score()
        
        logger.info(
            f"[Ecosystem Analyzer] Collected: "
            f"{len(fengshui_violations)} violations, "
            f"{len(guwu_executions)} test executions, "
            f"{len(guwu_flaky)} flaky tests"
        )
        
        return {
            'timeframe_days': days,
            'fengshui': {
                'violations': fengshui_violations,
                'summary': fengshui_summary,
                'score': fengshui_score,
                'violation_count': fengshui_summary.total_violations,
                'critical_count': fengshui_summary.critical_count,
                'high_count': fengshui_summary.high_count,
                'violations_by_type': fengshui_summary.violations_by_type,
                'violations_by_module': fengshui_summary.violations_by_module
            },
            'guwu': {
                'executions': guwu_executions,
                'flaky_tests': guwu_flaky,
                'summary': guwu_summary,
                'score': guwu_score,
                'test_count': guwu_summary.total_tests,
                'passing_count': guwu_summary.passing_tests,
                'failing_count': guwu_summary.failing_tests,
                'flaky_count': guwu_summary.flaky_tests,
                'slow_count': guwu_summary.slow_tests,
                'coverage': guwu_summary.coverage_percentage,
                'tests_by_type': guwu_summary.tests_by_type
            }
        }
    
    def get_module_correlation_data(self, module_name: str, days: int = 7) -> Dict:
        """
        Get both code and test data for a specific module
        
        Args:
            module_name: Module to analyze
            days: Number of days to look back
        
        Returns:
            Dictionary with module-specific data from both systems
        """
        logger.info(f"[Ecosystem Analyzer] Analyzing module: {module_name}")
        
        # Get Feng Shui violations for this module
        all_violations = self.fengshui.get_recent_violations(days)
        module_violations = [
            v for v in all_violations
            if v.get('module_name', '').lower() == module_name.lower()
        ]
        
        # Get Gu Wu tests for this module
        module_tests = self.guwu.get_tests_for_module(module_name, days)
        
        # Get flaky tests for this module
        all_flaky = self.guwu.get_flaky_tests(days)
        module_flaky = [
            f for f in all_flaky
            if module_name.lower() in f.get('test_file', '').lower()
        ]
        
        return {
            'module_name': module_name,
            'timeframe_days': days,
            'code_violations': module_violations,
            'violation_count': len(module_violations),
            'test_executions': module_tests,
            'test_count': len(module_tests),
            'flaky_tests': module_flaky,
            'flaky_count': len(module_flaky)
        }
    
    def identify_troubled_modules(self, days: int = 7) -> List[str]:
        """
        Identify modules with issues in BOTH code and tests
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of module names with cross-domain issues
        """
        logger.info("[Ecosystem Analyzer] Identifying troubled modules...")
        
        # Get modules with Feng Shui violations
        code_modules = self.fengshui.get_modules_with_issues(min_violations=3)
        
        # Get all test executions
        test_executions = self.guwu.get_recent_test_executions(days)
        
        # Count test failures by module
        test_issues_by_module = {}
        for test in test_executions:
            if test.get('outcome') == 'FAILED':
                test_file = test.get('test_file', '')
                # Extract module name from test file path
                for module in code_modules:
                    if module.lower() in test_file.lower():
                        test_issues_by_module[module] = test_issues_by_module.get(module, 0) + 1
        
        # Find modules with BOTH code and test issues
        troubled = [
            module for module in code_modules
            if module in test_issues_by_module and test_issues_by_module[module] >= 2
        ]
        
        logger.info(f"[Ecosystem Analyzer] Found {len(troubled)} troubled modules")
        return troubled
    
    def compare_quality_trends(self, current_days: int = 7, comparison_days: int = 14) -> Dict:
        """
        Compare current quality metrics to previous period
        
        Args:
            current_days: Recent period
            comparison_days: Previous period to compare against
        
        Returns:
            Dictionary with trend analysis
        """
        logger.info("[Ecosystem Analyzer] Analyzing quality trends...")
        
        # Current period
        current_data = self.collect_recent_data(current_days)
        
        # Previous period (comparison_days - current_days ago)
        # Note: This is simplified - in production we'd query specific date ranges
        previous_data = self.collect_recent_data(comparison_days)
        
        # Calculate trends
        fengshui_trend = current_data['fengshui']['score'] - previous_data['fengshui']['score']
        guwu_trend = current_data['guwu']['score'] - previous_data['guwu']['score']
        
        violation_trend = (
            current_data['fengshui']['violation_count'] - 
            previous_data['fengshui']['violation_count']
        )
        
        flaky_trend = (
            current_data['guwu']['flaky_count'] - 
            previous_data['guwu']['flaky_count']
        )
        
        return {
            'current_period_days': current_days,
            'comparison_period_days': comparison_days,
            'fengshui_score_change': fengshui_trend,
            'guwu_score_change': guwu_trend,
            'violation_count_change': violation_trend,
            'flaky_test_count_change': flaky_trend,
            'overall_trend': 'IMPROVING' if (fengshui_trend > 0 and guwu_trend > 0) else 'DECLINING',
            'current': current_data,
            'previous': previous_data
        }
    
    def get_quality_distribution(self, days: int = 7) -> Dict:
        """
        Get distribution of quality issues across the ecosystem
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dictionary with quality distribution statistics
        """
        data = self.collect_recent_data(days)
        
        # Code issue distribution
        violation_types = data['fengshui']['violations_by_type']
        top_code_issues = sorted(
            violation_types.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Test issue distribution
        test_types = data['guwu']['tests_by_type']
        
        return {
            'timeframe_days': days,
            'top_code_violation_types': dict(top_code_issues),
            'test_type_distribution': test_types,
            'modules_with_code_issues': len(data['fengshui']['violations_by_module']),
            'total_code_violations': data['fengshui']['violation_count'],
            'total_test_failures': data['guwu']['failing_count'],
            'total_flaky_tests': data['guwu']['flaky_count']
        }