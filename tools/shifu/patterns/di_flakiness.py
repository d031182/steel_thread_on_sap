"""
DI Violations → Flaky Tests Pattern
====================================

Pattern: Dependency Injection violations in code cause flaky (non-deterministic) tests.

Why: Hardwired dependencies make tests sensitive to execution order, state, and timing.
When code uses direct instantiation or global state instead of DI, tests can't reliably
control dependencies, leading to intermittent failures.

Evidence: Modules with 5+ DI violations typically have 40%+ test flakiness rate.

Severity: URGENT/HIGH - Flaky tests erode confidence in test suite.
"""

from typing import Dict, Optional, List
from .base_pattern import BasePattern, PatternMatch


class DIFlakinessPattern(BasePattern):
    """
    Detects correlation between DI violations and flaky tests
    
    Shi Fu's Teaching:
    "When dependencies are hardwired, tests become unpredictable.
     Like a house built without foundations, it stands... sometimes.
     Fix the root (DI), both code and tests become solid."
    """
    
    @property
    def pattern_name(self) -> str:
        return "DI_CAUSES_FLAKINESS"
    
    @property
    def pattern_description(self) -> str:
        return "Dependency Injection violations lead to flaky (non-deterministic) tests"
    
    def detect(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> Optional[PatternMatch]:
        """
        Detect DI → Flakiness correlation
        
        Algorithm:
        1. Find modules with DI violations (Feng Shui)
        2. Check test flakiness for same modules (Gu Wu)
        3. If both high, correlation exists
        """
        # Extract module-level data
        violated_modules = self._find_di_violated_modules(fengshui_data)
        flaky_test_modules = self._find_flaky_test_modules(guwu_data)
        
        # Find intersection (modules with BOTH issues)
        affected_modules = set(violated_modules.keys()) & set(flaky_test_modules.keys())
        
        if not affected_modules:
            return None  # No correlation
        
        # Analyze severity
        total_di_violations = sum(violated_modules[m] for m in affected_modules)
        avg_flakiness = sum(flaky_test_modules[m] for m in affected_modules) / len(affected_modules)
        
        # Calculate confidence
        confidence = self._calculate_di_flakiness_confidence(
            total_di_violations,
            avg_flakiness,
            len(affected_modules)
        )
        
        # Only report if confidence is high enough
        if confidence < 0.6:
            return None
        
        # Determine severity
        impact_score = (total_di_violations / (len(affected_modules) * 10)) * avg_flakiness
        severity = self.determine_severity(impact_score, len(affected_modules))
        
        # Build evidence
        fengshui_evidence = {
            'total_di_violations': total_di_violations,
            'affected_modules': list(affected_modules),
            'violations_per_module': {m: violated_modules[m] for m in affected_modules}
        }
        
        guwu_evidence = {
            'average_flakiness_rate': f"{avg_flakiness:.1%}",
            'affected_modules': list(affected_modules),
            'flakiness_per_module': {m: f"{flaky_test_modules[m]:.1%}" for m in affected_modules}
        }
        
        # Generate teaching
        root_cause = self._explain_root_cause(total_di_violations, avg_flakiness)
        recommendation = self._generate_di_recommendation(affected_modules, total_di_violations)
        
        return PatternMatch(
            pattern_name=self.pattern_name,
            confidence=confidence,
            severity=severity,
            fengshui_evidence=fengshui_evidence,
            guwu_evidence=guwu_evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            estimated_effort=self.estimate_effort(len(affected_modules)),
            combined_value="High - Fixing DI violations will stabilize tests automatically",
            affected_modules=list(affected_modules)
        )
    
    def _find_di_violated_modules(self, fengshui_data: Dict) -> Dict[str, int]:
        """
        Extract modules with DI violations
        
        Returns:
            Dict mapping module_name -> violation_count
        """
        violated_modules = {}
        
        # Extract from Feng Shui violation data
        violations = fengshui_data.get('violations', [])
        
        for violation in violations:
            if 'DI' in violation.get('type', '').upper() or 'DEPENDENCY' in violation.get('type', '').upper():
                module = violation.get('module', 'unknown')
                violated_modules[module] = violated_modules.get(module, 0) + 1
        
        # Filter: only modules with 5+ violations (pattern threshold)
        return {m: count for m, count in violated_modules.items() if count >= 5}
    
    def _find_flaky_test_modules(self, guwu_data: Dict) -> Dict[str, float]:
        """
        Extract modules with flaky tests
        
        Returns:
            Dict mapping module_name -> flakiness_rate (0.0-1.0)
        """
        flaky_modules = {}
        
        # Extract from Gu Wu test metrics
        test_results = guwu_data.get('test_results', [])
        
        for result in test_results:
            module = result.get('module', 'unknown')
            flakiness_rate = result.get('flakiness_rate', 0.0)
            
            # Pattern threshold: 40% flakiness
            if flakiness_rate >= 0.4:
                flaky_modules[module] = flakiness_rate
        
        return flaky_modules
    
    def _calculate_di_flakiness_confidence(
        self,
        di_violations: int,
        avg_flakiness: float,
        affected_module_count: int
    ) -> float:
        """
        Calculate confidence that DI violations CAUSE flakiness
        
        Confidence factors:
        - More DI violations = higher confidence
        - Higher flakiness rate = higher confidence
        - More affected modules = higher confidence (pattern, not coincidence)
        """
        # Base confidence from violation count (normalized to 0-1)
        violation_confidence = min(1.0, di_violations / 30.0)  # 30+ violations = max
        
        # Flakiness contribution (already 0-1)
        flakiness_confidence = avg_flakiness
        
        # Pattern strength (more modules = stronger evidence)
        pattern_confidence = min(1.0, affected_module_count / 5.0)  # 5+ modules = max
        
        # Weighted combination
        confidence = (
            violation_confidence * 0.4 +
            flakiness_confidence * 0.4 +
            pattern_confidence * 0.2
        )
        
        return confidence
    
    def _explain_root_cause(self, di_violations: int, avg_flakiness: float) -> str:
        """Generate root cause explanation"""
        return f"""
Hardwired dependencies in {di_violations} locations cause non-deterministic test behavior.
Tests sometimes pass (when mocks align with state) and sometimes fail (when state differs).
Average flakiness rate: {avg_flakiness:.1%}

Root Cause: Tests cannot reliably control dependencies through DI, leading to:
1. State leakage between tests
2. Order-dependent test execution
3. Timing-sensitive assertions
4. Non-deterministic mocking
"""
    
    def _generate_di_recommendation(self, modules: set, violations: int) -> str:
        """Generate actionable recommendation"""
        module_list = ', '.join(sorted(modules)[:3])
        if len(modules) > 3:
            module_list += f", and {len(modules) - 3} more"
        
        return f"""
IMMEDIATE ACTION:
1. Fix DI violations in: {module_list}
2. Use constructor injection for dependencies
3. Tests will automatically become deterministic

IMPLEMENTATION:
- Replace direct instantiation with dependency injection
- Use interfaces/protocols for loose coupling
- Pass dependencies via __init__, not hardwired access

EXPECTED OUTCOME:
- Flaky tests will stabilize automatically (no test code changes needed)
- {violations} DI violations fixed
- Test success rate improves from ~{100 - avg_flakiness * 100:.0f}% to 95%+

NOTE: Fixing the ROOT (DI) heals BOTH branches (code + tests).
"""