"""
Action Executor for Gu Wu Agent

Implements the "Act" part of ReAct pattern.
Executes testing actions based on reasoning decisions.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import subprocess

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from tests.guwu.gap_analyzer import TestGapAnalyzer
from tests.guwu.predictor import FailurePredictor
from tests.guwu.autofix import AutoFixGenerator


@dataclass
class ActionResult:
    """
    Result of executing an action
    
    Contains:
    - What action was executed
    - Whether it succeeded
    - Data produced by action
    - Time taken
    """
    action: str
    success: bool
    data: Dict[str, Any]
    duration: float
    timestamp: datetime
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging"""
        return {
            'action': self.action,
            'success': self.success,
            'data': self.data,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'error': self.error
        }


class ActionExecutor:
    """
    Executes testing actions autonomously
    
    Available actions:
    - analyze_gaps: Find untested code
    - generate_fixes: Create fix suggestions
    - predict_failures: Predict which tests will fail
    - optimize_performance: Speed up slow tests
    - verify_coverage: Check coverage metrics
    - run_tests: Execute specific tests
    """
    
    def __init__(self, db_path: str, verbose: bool = False):
        """
        Initialize action executor
        
        Args:
            db_path: Path to Gu Wu metrics database
            verbose: Enable detailed logging
        """
        self.db_path = db_path
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gu Wu components
        self.gap_analyzer = TestGapAnalyzer(db_path)
        self.predictor = FailurePredictor(db_path)
        self.autofix = AutoFixGenerator(db_path)
        
        # Action history for learning
        self.action_history: List[ActionResult] = []
    
    def execute(self, action: str, params: Optional[Dict] = None) -> ActionResult:
        """
        Execute an action
        
        Args:
            action: Action name to execute
            params: Optional parameters for action
        
        Returns:
            ActionResult with execution details
        """
        params = params or {}
        start_time = datetime.now()
        
        if self.verbose:
            self.logger.info(f"[Gu Wu Agent] EXECUTING: {action}")
        
        try:
            # Route to appropriate handler
            if action == 'analyze_gaps':
                data = self._execute_analyze_gaps(params)
                success = True
            
            elif action == 'generate_targeted_tests':
                data = self._execute_generate_targeted_tests(params)
                success = True
            
            elif action == 'generate_critical_tests':
                data = self._execute_generate_critical_tests(params)
                success = True
            
            elif action == 'analyze_flaky_patterns':
                data = self._execute_analyze_flaky_patterns(params)
                success = True
            
            elif action == 'generate_flaky_fixes':
                data = self._execute_generate_flaky_fixes(params)
                success = True
            
            elif action == 'analyze_performance_bottlenecks':
                data = self._execute_analyze_performance_bottlenecks(params)
                success = True
            
            elif action == 'generate_optimizations':
                data = self._execute_generate_optimizations(params)
                success = True
            
            elif action == 'predict_failures':
                data = self._execute_predict_failures(params)
                success = True
            
            elif action == 'run_tests':
                data = self._execute_run_tests(params)
                success = data.get('exit_code', 1) == 0
            
            elif action == 'complete':
                data = {'message': 'Goal achieved', 'status': 'complete'}
                success = True
            
            elif action == 'verify_coverage':
                data = self._execute_verify_coverage(params)
                success = True
            
            else:
                data = {'error': f'Unknown action: {action}'}
                success = False
            
            error = None
        
        except Exception as e:
            self.logger.error(f"[Gu Wu Agent] Action failed: {e}")
            data = {'error': str(e)}
            success = False
            error = str(e)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Create result
        result = ActionResult(
            action=action,
            success=success,
            data=data,
            duration=duration,
            timestamp=start_time,
            error=error
        )
        
        # Store for learning
        self.action_history.append(result)
        
        if self.verbose:
            self._log_action_result(result)
        
        return result
    
    def _execute_analyze_gaps(self, params: Dict) -> Dict:
        """Execute gap analysis"""
        self.logger.info("[Gu Wu] Analyzing test coverage gaps...")
        
        gaps = self.gap_analyzer.analyze()
        
        return {
            'total_gaps': len(gaps),
            'critical_gaps': len([g for g in gaps if g.priority == 'CRITICAL']),
            'high_gaps': len([g for g in gaps if g.priority == 'HIGH']),
            'gaps': gaps[:10]  # Return top 10 for review
        }
    
    def _execute_generate_targeted_tests(self, params: Dict) -> Dict:
        """Generate tests for specific areas"""
        self.logger.info("[Gu Wu] Generating targeted tests...")
        
        # Use gap analyzer to find specific gaps
        gaps = self.gap_analyzer.analyze()
        high_priority = [g for g in gaps if g.priority in ['CRITICAL', 'HIGH']][:5]
        
        # Generate test templates
        templates = []
        for gap in high_priority:
            template = self.gap_analyzer._generate_test_template(gap)
            templates.append({
                'file': gap.file_path,
                'function': gap.function_name,
                'template': template
            })
        
        return {
            'tests_generated': len(templates),
            'templates': templates
        }
    
    def _execute_generate_critical_tests(self, params: Dict) -> Dict:
        """Generate tests for critical gaps only"""
        self.logger.info("[Gu Wu] Generating critical tests...")
        
        gaps = self.gap_analyzer.analyze()
        critical = [g for g in gaps if g.priority == 'CRITICAL']
        
        templates = []
        for gap in critical:
            template = self.gap_analyzer._generate_test_template(gap)
            templates.append({
                'file': gap.file_path,
                'function': gap.function_name,
                'complexity': gap.complexity,
                'template': template
            })
        
        return {
            'critical_tests_generated': len(templates),
            'templates': templates
        }
    
    def _execute_analyze_flaky_patterns(self, params: Dict) -> Dict:
        """Analyze patterns in flaky tests"""
        self.logger.info("[Gu Wu] Analyzing flaky test patterns...")
        
        # Get flaky tests from metrics
        flaky_tests = self._get_flaky_tests()
        
        # Analyze common patterns
        patterns = self._find_common_patterns(flaky_tests)
        
        return {
            'flaky_tests_found': len(flaky_tests),
            'patterns_identified': len(patterns),
            'patterns': patterns,
            'tests': flaky_tests[:10]  # Top 10
        }
    
    def _execute_generate_flaky_fixes(self, params: Dict) -> Dict:
        """Generate fixes for flaky tests"""
        self.logger.info("[Gu Wu] Generating flaky test fixes...")
        
        flaky_tests = self._get_flaky_tests()
        
        fixes = []
        for test in flaky_tests[:5]:  # Top 5 flaky tests
            fix = self.autofix.generate_fix(
                test_id=test['test_id'],
                error_message='Flaky test detected',
                traceback=test.get('last_failure_traceback', '')
            )
            if fix:
                fixes.append(fix)
        
        return {
            'fixes_generated': len(fixes),
            'fixes': fixes
        }
    
    def _execute_analyze_performance_bottlenecks(self, params: Dict) -> Dict:
        """Analyze performance bottlenecks"""
        self.logger.info("[Gu Wu] Analyzing performance bottlenecks...")
        
        slow_tests = self._get_slow_tests()
        
        # Group by common factors
        bottlenecks = self._identify_bottlenecks(slow_tests)
        
        return {
            'slow_tests_found': len(slow_tests),
            'bottlenecks_identified': len(bottlenecks),
            'bottlenecks': bottlenecks,
            'tests': slow_tests[:10]  # Top 10 slowest
        }
    
    def _execute_generate_optimizations(self, params: Dict) -> Dict:
        """Generate optimization suggestions"""
        self.logger.info("[Gu Wu] Generating optimizations...")
        
        slow_tests = self._get_slow_tests()
        
        optimizations = []
        for test in slow_tests[:5]:  # Top 5 slowest
            suggestions = self._suggest_optimization(test)
            optimizations.append({
                'test_id': test['test_id'],
                'current_duration': test['duration'],
                'suggestions': suggestions
            })
        
        return {
            'optimizations_generated': len(optimizations),
            'optimizations': optimizations
        }
    
    def _execute_predict_failures(self, params: Dict) -> Dict:
        """Predict which tests will fail"""
        self.logger.info("[Gu Wu] Predicting test failures...")
        
        predictions = self.predictor.predict_failures()
        high_risk = [p for p in predictions if p.probability > 0.7]
        
        return {
            'predictions_made': len(predictions),
            'high_risk_tests': len(high_risk),
            'predictions': predictions[:10],  # Top 10 risky
            'high_risk': high_risk
        }
    
    def _execute_run_tests(self, params: Dict) -> Dict:
        """Execute specific tests"""
        tests = params.get('tests', [])
        
        if not tests:
            return {'error': 'No tests specified', 'exit_code': 1}
        
        self.logger.info(f"[Gu Wu] Running {len(tests)} tests...")
        
        # Run via pytest
        result = subprocess.run(
            ['pytest'] + tests + ['-v'],
            capture_output=True,
            text=True
        )
        
        return {
            'tests_run': len(tests),
            'exit_code': result.returncode,
            'stdout': result.stdout[-1000:],  # Last 1000 chars
            'stderr': result.stderr[-1000:] if result.stderr else None
        }
    
    def _execute_verify_coverage(self, params: Dict) -> Dict:
        """Verify test coverage"""
        self.logger.info("[Gu Wu] Verifying coverage...")
        
        # Run pytest with coverage
        result = subprocess.run(
            ['pytest', '--cov=modules', '--cov=core', '--cov-report=term-missing'],
            capture_output=True,
            text=True
        )
        
        # Parse coverage from output
        coverage_pct = self._parse_coverage_from_output(result.stdout)
        
        return {
            'coverage_percentage': coverage_pct,
            'verification_passed': result.returncode == 0,
            'output': result.stdout[-500:]
        }
    
    def _get_flaky_tests(self) -> List[Dict]:
        """Get flaky tests from database"""
        # Query metrics database for flaky tests
        # This is a placeholder - would query actual database
        return []
    
    def _get_slow_tests(self, threshold: float = 5.0) -> List[Dict]:
        """Get slow tests from database"""
        # Query metrics database for slow tests
        # This is a placeholder - would query actual database
        return []
    
    def _find_common_patterns(self, flaky_tests: List[Dict]) -> List[Dict]:
        """Find common patterns in flaky tests"""
        # Analyze error messages, modules, timing patterns
        # This is a placeholder - would do actual analysis
        return []
    
    def _identify_bottlenecks(self, slow_tests: List[Dict]) -> List[Dict]:
        """Identify performance bottlenecks"""
        # Analyze what makes tests slow (I/O, computation, etc.)
        # This is a placeholder - would do actual analysis
        return []
    
    def _suggest_optimization(self, test: Dict) -> List[str]:
        """Suggest optimizations for a test"""
        suggestions = []
        
        duration = test.get('duration', 0)
        
        if duration > 10:
            suggestions.append("Consider mocking external dependencies")
            suggestions.append("Check for unnecessary database operations")
        
        if duration > 5:
            suggestions.append("Use fixtures instead of setup/teardown")
            suggestions.append("Consider parallelization")
        
        return suggestions
    
    def _parse_coverage_from_output(self, output: str) -> float:
        """Parse coverage percentage from pytest output"""
        import re
        
        # Look for "TOTAL" line with coverage percentage
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if match:
            return float(match.group(1)) / 100.0
        
        return 0.0
    
    def _log_action_result(self, result: ActionResult):
        """Log action result for transparency"""
        self.logger.info("=" * 60)
        self.logger.info("[Gu Wu Agent] ACTION RESULT")
        self.logger.info("=" * 60)
        self.logger.info(f"Action: {result.action}")
        self.logger.info(f"Success: {result.success}")
        self.logger.info(f"Duration: {result.duration:.2f}s")
        if result.error:
            self.logger.error(f"Error: {result.error}")
        else:
            self.logger.info(f"Data: {result.data}")
        self.logger.info("=" * 60)
    
    def get_action_summary(self) -> Dict:
        """Get summary of actions executed"""
        if not self.action_history:
            return {'total_actions': 0, 'success_rate': 0.0}
        
        successful = sum(1 for a in self.action_history if a.success)
        
        return {
            'total_actions': len(self.action_history),
            'success_rate': successful / len(self.action_history),
            'total_duration': sum(a.duration for a in self.action_history),
            'actions_taken': [a.action for a in self.action_history],
            'success_count': successful,
            'failure_count': len(self.action_history) - successful
        }


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    executor = ActionExecutor(db_path='tests/guwu/metrics.db', verbose=True)
    
    # Example 1: Analyze gaps
    result = executor.execute('analyze_gaps')
    print(f"\nAction: {result.action}")
    print(f"Success: {result.success}")
    print(f"Gaps found: {result.data.get('total_gaps', 0)}")
    
    # Example 2: Predict failures
    result = executor.execute('predict_failures')
    print(f"\nAction: {result.action}")
    print(f"Predictions: {result.data.get('predictions_made', 0)}")