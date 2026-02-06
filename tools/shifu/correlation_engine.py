"""
Correlation Engine: Pattern Detection Across Code and Tests
===========================================================

The Master's wisdom - finding connections between code quality and test quality.
"""

import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class CorrelationPattern:
    """A detected pattern correlating code and test issues"""
    id: str
    pattern_name: str
    confidence: float  # 0.0-1.0
    severity: str  # URGENT/HIGH/MEDIUM/LOW
    fengshui_evidence: str
    guwu_evidence: str
    root_cause: str
    recommendation: str
    estimated_effort: str
    combined_value: str
    timestamp: str


class CorrelationEngine:
    """
    Pattern detection engine for cross-domain quality issues
    
    Implements Shi Fu's core wisdom: seeing connections between
    code architecture problems and test quality problems.
    """
    
    def __init__(self):
        """Initialize correlation engine"""
        self.patterns_detected = []
    
    def detect_patterns(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> List[CorrelationPattern]:
        """
        Apply pattern detection algorithms to find correlations
        
        Args:
            fengshui_data: Code quality data from Feng Shui
            guwu_data: Test quality data from Gu Wu
        
        Returns:
            List of detected correlation patterns
        """
        logger.info("[Correlation Engine] Analyzing cross-domain patterns...")
        
        correlations = []
        
        # Pattern 1: DI Violations → Flaky Tests
        di_flaky = self._detect_di_flakiness_pattern(fengshui_data, guwu_data)
        if di_flaky:
            correlations.append(di_flaky)
        
        # Pattern 2: High Complexity → Low Coverage
        complexity_coverage = self._detect_complexity_coverage_pattern(fengshui_data, guwu_data)
        if complexity_coverage:
            correlations.append(complexity_coverage)
        
        # Pattern 3: Security Issues → Test Gaps
        security_gaps = self._detect_security_test_gaps(fengshui_data, guwu_data)
        if security_gaps:
            correlations.append(security_gaps)
        
        # Pattern 4: Performance Issues → Slow Tests
        performance_slow = self._detect_performance_slow_tests(fengshui_data, guwu_data)
        if performance_slow:
            correlations.append(performance_slow)
        
        # Pattern 5: Module Health → Test Health
        module_test_health = self._detect_module_test_correlation(fengshui_data, guwu_data)
        if module_test_health:
            correlations.append(module_test_health)
        
        logger.info(f"[Correlation Engine] Detected {len(correlations)} patterns")
        self.patterns_detected = correlations
        
        return correlations
    
    def _detect_di_flakiness_pattern(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> CorrelationPattern:
        """
        Pattern: DI violations cause flaky tests
        
        When dependencies are hardwired, tests become non-deterministic
        because they depend on global state.
        """
        # Count DI violations
        violations_by_type = fengshui_data.get('violations_by_type', {})
        di_violations = violations_by_type.get('DI_VIOLATION', 0)
        
        # Count flaky tests
        flaky_count = guwu_data.get('flaky_count', 0)
        
        # Check if correlation exists (both issues present)
        if di_violations >= 3 and flaky_count >= 2:
            confidence = min(1.0, (di_violations * flaky_count) / 50.0)  # Normalize
            
            return CorrelationPattern(
                id="DI_FLAKINESS_001",
                pattern_name="DI Violations Causing Flaky Tests",
                confidence=confidence,
                severity="URGENT" if di_violations >= 10 else "HIGH",
                fengshui_evidence=f"Found {di_violations} DI violations across modules. "
                                 f"Dependencies are hardwired (.connection, .service, .db_path access).",
                guwu_evidence=f"Detected {flaky_count} flaky tests with inconsistent pass/fail patterns. "
                             f"Tests show {guwu_data.get('flaky_count', 0)}/{guwu_data.get('test_count', 1)} flakiness rate.",
                root_cause="Hardwired dependencies create hidden coupling. Tests pass/fail based on "
                          "global state rather than explicit dependencies. This makes tests non-deterministic.",
                recommendation="Fix DI violations first using Dependency Injection pattern:\n"
                             "1. Pass dependencies via constructor\n"
                             "2. Use interfaces from core.interfaces\n"
                             "3. Remove direct .connection/.service access\n"
                             "Result: Flaky tests will stabilize automatically when dependencies are explicit.",
                estimated_effort="2-4 hours (fix DI violations)",
                combined_value=f"Code quality +{di_violations * 2} points, "
                              f"Test reliability +{flaky_count * 10}% stability",
                timestamp=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_complexity_coverage_pattern(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> CorrelationPattern:
        """
        Pattern: High code complexity correlates with low test coverage
        
        Complex code is harder to test, leading to coverage gaps.
        """
        # Check for complexity violations
        violations_by_type = fengshui_data.get('violations_by_type', {})
        complexity_issues = violations_by_type.get('HIGH_COMPLEXITY', 0)
        
        # Check coverage
        coverage = guwu_data.get('coverage', 70.0)
        
        if complexity_issues >= 5 and coverage < 70.0:
            confidence = 0.8
            
            return CorrelationPattern(
                id="COMPLEXITY_COVERAGE_001",
                pattern_name="High Complexity Reducing Test Coverage",
                confidence=confidence,
                severity="HIGH",
                fengshui_evidence=f"Found {complexity_issues} functions/methods with high cyclomatic complexity. "
                                 f"Code is difficult to understand and modify.",
                guwu_evidence=f"Test coverage at {coverage:.1f}%, below target of 70%. "
                             f"Complex code has insufficient test scenarios.",
                root_cause="Complex code has many execution paths. Each path needs testing, but "
                          "complexity makes it hard to write comprehensive tests. Result: coverage gaps.",
                recommendation="Refactor complex functions into smaller, testable units:\n"
                             "1. Extract methods (break large functions)\n"
                             "2. Reduce branching (simplify conditionals)\n"
                             "3. Apply Single Responsibility Principle\n"
                             "Result: Simpler code is easier to test thoroughly.",
                estimated_effort="4-6 hours (refactoring)",
                combined_value=f"Code maintainability +{complexity_issues * 3} points, "
                              f"Test coverage +{(70 - coverage):.1f}% potential gain",
                timestamp=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_security_test_gaps(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> CorrelationPattern:
        """
        Pattern: Security violations indicate missing security tests
        """
        violations_by_type = fengshui_data.get('violations_by_type', {})
        security_issues = violations_by_type.get('SECURITY_ISSUE', 0)
        
        # Check for security-focused tests
        tests_by_type = guwu_data.get('tests_by_type', {})
        security_tests = tests_by_type.get('security', 0)
        
        if security_issues >= 3 and security_tests < 5:
            confidence = 0.85
            
            return CorrelationPattern(
                id="SECURITY_GAPS_001",
                pattern_name="Security Issues Lacking Test Coverage",
                confidence=confidence,
                severity="URGENT",
                fengshui_evidence=f"Detected {security_issues} security vulnerabilities: "
                                 f"SQL injection risks, hardcoded secrets, or missing validation.",
                guwu_evidence=f"Only {security_tests} security-focused tests exist. "
                             f"Critical attack vectors are untested.",
                root_cause="Security issues exist in code, but no tests verify the fixes or prevent "
                          "regressions. Vulnerabilities can reappear undetected.",
                recommendation="Create security test suite immediately:\n"
                             "1. Test SQL injection prevention (parameterized queries)\n"
                             "2. Test authentication/authorization flows\n"
                             "3. Test input validation (XSS, CSRF)\n"
                             "4. Add security tests to CI/CD pipeline\n"
                             "Result: Security fixes verified, regressions prevented.",
                estimated_effort="3-5 hours (security test suite)",
                combined_value=f"Security posture +{security_issues * 5} points, "
                              f"Risk reduction: {security_issues} vulnerabilities protected",
                timestamp=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_performance_slow_tests(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> CorrelationPattern:
        """
        Pattern: Performance issues (N+1 queries) cause slow tests
        """
        violations_by_type = fengshui_data.get('violations_by_type', {})
        performance_issues = violations_by_type.get('PERFORMANCE_ISSUE', 0)
        
        slow_tests = guwu_data.get('slow_count', 0)
        
        if performance_issues >= 3 and slow_tests >= 5:
            confidence = 0.75
            
            return CorrelationPattern(
                id="PERFORMANCE_SLOW_001",
                pattern_name="Performance Issues Slowing Test Suite",
                confidence=confidence,
                severity="MEDIUM",
                fengshui_evidence=f"Found {performance_issues} performance problems: "
                                 f"N+1 queries, nested loops, missing caching.",
                guwu_evidence=f"{slow_tests} tests exceed 5-second threshold. "
                             f"Average execution time: {guwu_data.get('avg_execution_time', 0):.2f}ms. "
                             f"Test suite too slow for rapid feedback.",
                root_cause="Inefficient code patterns (N+1 queries, missing indexes) execute in tests. "
                          "Tests are slow because underlying code is slow.",
                recommendation="Optimize code performance:\n"
                             "1. Fix N+1 queries (use JOIN or prefetch)\n"
                             "2. Add database indexes\n"
                             "3. Implement caching where appropriate\n"
                             "Result: Code runs faster, tests run faster, better developer experience.",
                estimated_effort="2-4 hours (performance optimization)",
                combined_value=f"Code performance +{performance_issues * 4}x faster, "
                              f"Test suite -{slow_tests * 2}s execution time",
                timestamp=datetime.now().isoformat()
            )
        
        return None
    
    def _detect_module_test_correlation(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> CorrelationPattern:
        """
        Pattern: Modules with many violations have failing tests
        
        General correlation between code quality and test health.
        """
        violations_by_module = fengshui_data.get('violations_by_module', {})
        
        if not violations_by_module:
            return None
        
        # Find module with most violations
        worst_module = max(violations_by_module.items(), key=lambda x: x[1])
        module_name, violation_count = worst_module
        
        if violation_count >= 10:
            # Check if this module has test issues
            test_count = guwu_data.get('test_count', 0)
            failing_count = guwu_data.get('failing_count', 0)
            
            if failing_count >= 3:
                confidence = 0.7
                
                return CorrelationPattern(
                    id="MODULE_HEALTH_001",
                    pattern_name=f"Module '{module_name}' Quality Ecosystem Issue",
                    confidence=confidence,
                    severity="HIGH",
                    fengshui_evidence=f"Module '{module_name}' has {violation_count} code violations. "
                                     f"Top issues: {', '.join(list(violations_by_module.keys())[:3])}",
                    guwu_evidence=f"Module has {failing_count} failing tests out of {test_count} total. "
                                 f"Failure rate: {(failing_count/test_count*100) if test_count > 0 else 0:.1f}%",
                    root_cause=f"Module '{module_name}' has accumulated technical debt. Poor code quality "
                              f"makes it hard to maintain, leading to test failures.",
                    recommendation=f"Comprehensive module refactoring needed:\n"
                                 f"1. Run Feng Shui on module: python -m tools.fengshui.react_agent\n"
                                 f"2. Fix critical violations first\n"
                                 f"3. Update/fix failing tests\n"
                                 f"4. Add missing test coverage\n"
                                 f"Result: Module becomes healthy, maintainable foundation.",
                    estimated_effort="6-8 hours (module refactoring)",
                    combined_value=f"Module quality +{violation_count} points fixed, "
                                  f"Test reliability +{failing_count} tests stabilized",
                    timestamp=datetime.now().isoformat()
                )
        
        return None
    
    def get_prioritized_insights(self) -> List[CorrelationPattern]:
        """
        Get detected patterns sorted by priority
        
        Returns:
            List of patterns sorted by severity and confidence
        """
        severity_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        
        sorted_patterns = sorted(
            self.patterns_detected,
            key=lambda p: (severity_order.get(p.severity, 3), -p.confidence)
        )
        
        return sorted_patterns
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary of correlation analysis
        
        Returns:
            Dictionary with analysis statistics
        """
        if not self.patterns_detected:
            return {
                'total_patterns': 0,
                'urgent': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'avg_confidence': 0.0
            }
        
        severity_counts = {}
        for pattern in self.patterns_detected:
            severity = pattern.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        avg_confidence = sum(p.confidence for p in self.patterns_detected) / len(self.patterns_detected)
        
        return {
            'total_patterns': len(self.patterns_detected),
            'urgent': severity_counts.get('URGENT', 0),
            'high': severity_counts.get('HIGH', 0),
            'medium': severity_counts.get('MEDIUM', 0),
            'low': severity_counts.get('LOW', 0),
            'avg_confidence': avg_confidence,
            'patterns': [
                {
                    'id': p.id,
                    'name': p.pattern_name,
                    'severity': p.severity,
                    'confidence': p.confidence
                }
                for p in self.patterns_detected
            ]
        }