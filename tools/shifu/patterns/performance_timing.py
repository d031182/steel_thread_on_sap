"""
Performance Issues → Slow Tests Pattern
========================================

Pattern: Performance problems in code (N+1 queries, nested loops) cause slow test execution.

Why: Inefficient code makes every test that exercises it slow.
Tests become a bottleneck, reducing developer productivity.

Evidence: Modules with N+1 queries have 5-10x slower tests.

Severity: MEDIUM - Affects developer experience, not production directly.
"""

from typing import Dict, Optional
from .base_pattern import BasePattern, PatternMatch


class PerformanceTimingPattern(BasePattern):
    """
    Detects correlation between code performance issues and slow tests
    
    Shi Fu's Teaching:
    "Slow code makes slow tests. Fast code makes fast tests.
     The student complains tests are slow.
     The master asks: why is your code slow?"
    """
    
    @property
    def pattern_name(self) -> str:
        return "PERFORMANCE_ISSUES_SLOW_TESTS"
    
    @property
    def pattern_description(self) -> str:
        return "Performance problems in code cause slow test execution"
    
    def detect(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> Optional[PatternMatch]:
        """
        Detect Performance Issues → Slow Tests correlation
        
        Algorithm:
        1. Find performance issues (Feng Shui): N+1 queries, nested loops
        2. Find slow tests for same modules (Gu Wu)
        3. If both exist, correlation likely
        """
        # Extract data
        perf_issues = self._find_performance_issues(fengshui_data)
        slow_tests = self._find_slow_tests(guwu_data)
        
        # Find correlation (modules with BOTH)
        affected_modules = set(perf_issues.keys()) & set(slow_tests.keys())
        
        if not affected_modules:
            return None
        
        # Calculate metrics
        total_perf_issues = sum(perf_issues[m] for m in affected_modules)
        avg_test_time = sum(slow_tests[m] for m in affected_modules) / len(affected_modules)
        
        # Calculate confidence
        confidence = self._calculate_performance_confidence(
            total_perf_issues,
            avg_test_time,
            len(affected_modules)
        )
        
        if confidence < 0.6:
            return None
        
        # Determine severity
        impact_score = (total_perf_issues / len(affected_modules)) * (avg_test_time / 10.0)
        severity = self.determine_severity(impact_score, len(affected_modules))
        
        # Build evidence
        fengshui_evidence = {
            'total_performance_issues': total_perf_issues,
            'affected_modules': list(affected_modules),
            'issues_per_module': {m: perf_issues[m] for m in affected_modules}
        }
        
        guwu_evidence = {
            'average_test_time': f"{avg_test_time:.2f}s",
            'affected_modules': list(affected_modules),
            'time_per_module': {m: f"{slow_tests[m]:.2f}s" for m in affected_modules}
        }
        
        # Generate teaching
        root_cause = self._explain_root_cause(total_perf_issues, avg_test_time)
        recommendation = self._generate_recommendation(affected_modules, perf_issues, slow_tests)
        
        return PatternMatch(
            pattern_name=self.pattern_name,
            confidence=confidence,
            severity=severity,
            fengshui_evidence=fengshui_evidence,
            guwu_evidence=guwu_evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            estimated_effort=self.estimate_effort(len(affected_modules)),
            combined_value="Medium - Improves developer experience and code efficiency",
            affected_modules=list(affected_modules)
        )
    
    def _find_performance_issues(self, fengshui_data: Dict) -> Dict[str, int]:
        """Extract performance issues from Feng Shui"""
        perf_issues = {}
        
        violations = fengshui_data.get('violations', [])
        
        for violation in violations:
            vtype = violation.get('type', '').upper()
            if any(keyword in vtype for keyword in ['PERFORMANCE', 'N+1', 'LOOP', 'QUERY']):
                module = violation.get('module', 'unknown')
                perf_issues[module] = perf_issues.get(module, 0) + 1
        
        # Filter: only modules with 2+ performance issues
        return {m: count for m, count in perf_issues.items() if count >= 2}
    
    def _find_slow_tests(self, guwu_data: Dict) -> Dict[str, float]:
        """Extract slow tests from Gu Wu"""
        slow_tests = {}
        
        test_results = guwu_data.get('test_results', [])
        
        for test in test_results:
            module = test.get('module', 'unknown')
            duration = test.get('duration', 0.0)
            
            # Pattern threshold: tests taking >5 seconds
            if duration > 5.0:
                # Track slowest test per module
                if module not in slow_tests or duration > slow_tests[module]:
                    slow_tests[module] = duration
        
        return slow_tests
    
    def _calculate_performance_confidence(
        self,
        perf_issues: int,
        avg_test_time: float,
        affected_count: int
    ) -> float:
        """Calculate confidence for performance correlation"""
        # Performance issue contribution
        issue_confidence = min(1.0, perf_issues / 10.0)  # 10+ issues = max
        
        # Test slowness contribution (normalize: 10s = max)
        slowness_confidence = min(1.0, avg_test_time / 10.0)
        
        # Pattern strength
        pattern_confidence = min(1.0, affected_count / 5.0)
        
        # Weighted combination
        confidence = (
            issue_confidence * 0.4 +
            slowness_confidence * 0.4 +
            pattern_confidence * 0.2
        )
        
        return confidence
    
    def _explain_root_cause(self, perf_issues: int, avg_test_time: float) -> str:
        """Generate root cause explanation"""
        return f"""
{perf_issues} performance issues in code cause tests to run slowly (avg: {avg_test_time:.2f}s).

Root Cause: Inefficient code patterns:
1. N+1 database queries (fetch in loop instead of batch)
2. Nested loops with poor complexity (O(n²) or worse)
3. Missing database indexes
4. Unnecessary data loading

Every test that exercises this code suffers:
- Slow feedback loop (developers wait)
- CI/CD pipeline delays (builds take longer)
- Developer frustration (tests become bottleneck)

This is a CODE problem manifesting as a TEST problem.
Fix the code, tests automatically speed up.
"""
    
    def _generate_recommendation(self, modules: set, perf_issues: Dict, slow_tests: Dict) -> str:
        """Generate actionable recommendation"""
        worst_module = max(modules, key=lambda m: slow_tests[m])
        worst_time = slow_tests[worst_module]
        worst_issues = perf_issues[worst_module]
        
        return f"""
IMMEDIATE ACTION:
1. Profile slowest module: {worst_module} ({worst_time:.2f}s tests, {worst_issues} perf issues)
2. Fix identified performance issues
3. Watch tests speed up automatically

OPTIMIZATION STRATEGIES:
- Batch database queries (eliminate N+1 pattern)
- Add database indexes (speed up lookups)
- Cache expensive computations (avoid redundant work)
- Use lazy loading (don't fetch what you don't need)
- Replace nested loops with sets/dicts (O(n²) → O(n))

EXPECTED OUTCOME:
- Test execution time: {worst_time:.2f}s → <1.0s (5-10x speedup)
- CI/CD pipeline faster
- Developer productivity increases
- Production code also benefits (same optimizations)

MEASUREMENT:
Before: pytest tests/test_{worst_module}.py  # Note current time
After optimization: Re-run and compare
Target: <1s for unit tests, <5s for integration tests

PHILOSOPHY:
"The master does not speed up tests with mocks and shortcuts.
 The master optimizes code, and tests run fast naturally."
"""