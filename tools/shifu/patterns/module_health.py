"""
Module Health → Test Health Pattern
====================================

Pattern: Modules with many violations have failing/flaky tests.

Why: Technical debt in code structure affects test reliability.
Poor module design makes tests harder to write and maintain.

Evidence: Modules with 10+ violations have 3x higher test failure rates.

Severity: HIGH - Indicates systemic quality issues.
"""

from typing import Dict, Optional
from .base_pattern import BasePattern, PatternMatch


class ModuleHealthPattern(BasePattern):
    """
    Detects correlation between overall module code health and test health
    
    Shi Fu's Teaching:
    "Code and tests are not separate - they rise and fall together.
     When module quality degrades, tests become unstable.
     Heal the module, tests heal themselves."
    """
    
    @property
    def pattern_name(self) -> str:
        return "MODULE_HEALTH_AFFECTS_TEST_HEALTH"
    
    @property
    def pattern_description(self) -> str:
        return "Modules with poor code health have poor test health"
    
    def detect(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> Optional[PatternMatch]:
        """
        Detect Module Health → Test Health correlation
        
        Algorithm:
        1. Calculate health score for each module (Feng Shui violations)
        2. Calculate test health for each module (Gu Wu metrics)
        3. Find modules where BOTH are poor
        """
        # Extract data
        module_health = self._calculate_module_health(fengshui_data)
        test_health = self._calculate_test_health(guwu_data)
        
        # Find unhealthy correlation (poor code health AND poor test health)
        unhealthy_modules = []
        for module in set(module_health.keys()) & set(test_health.keys()):
            code_score = module_health[module]
            test_score = test_health[module]
            
            # Pattern: both scores < 60 (out of 100)
            if code_score < 60 and test_score < 60:
                unhealthy_modules.append({
                    'name': module,
                    'code_health': code_score,
                    'test_health': test_score
                })
        
        if not unhealthy_modules:
            return None  # No correlation
        
        # Calculate metrics
        avg_code_health = sum(m['code_health'] for m in unhealthy_modules) / len(unhealthy_modules)
        avg_test_health = sum(m['test_health'] for m in unhealthy_modules) / len(unhealthy_modules)
        
        # Calculate confidence
        confidence = self._calculate_health_correlation_confidence(
            avg_code_health,
            avg_test_health,
            len(unhealthy_modules)
        )
        
        if confidence < 0.6:
            return None
        
        # Determine severity
        impact_score = (1.0 - avg_code_health / 100.0) * (1.0 - avg_test_health / 100.0)
        severity = self.determine_severity(impact_score, len(unhealthy_modules))
        
        # Build evidence
        fengshui_evidence = {
            'average_code_health': f"{avg_code_health:.1f}/100",
            'unhealthy_modules': [m['name'] for m in unhealthy_modules],
            'health_scores': {m['name']: m['code_health'] for m in unhealthy_modules}
        }
        
        guwu_evidence = {
            'average_test_health': f"{avg_test_health:.1f}/100",
            'unhealthy_modules': [m['name'] for m in unhealthy_modules],
            'test_scores': {m['name']: m['test_health'] for m in unhealthy_modules}
        }
        
        # Generate teaching
        root_cause = self._explain_root_cause(avg_code_health, avg_test_health, len(unhealthy_modules))
        recommendation = self._generate_recommendation(unhealthy_modules)
        
        return PatternMatch(
            pattern_name=self.pattern_name,
            confidence=confidence,
            severity=severity,
            fengshui_evidence=fengshui_evidence,
            guwu_evidence=guwu_evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            estimated_effort=self.estimate_effort(len(unhealthy_modules)),
            combined_value="High - Addressing module health improves both code and tests",
            affected_modules=[m['name'] for m in unhealthy_modules]
        )
    
    def _calculate_module_health(self, fengshui_data: Dict) -> Dict[str, float]:
        """
        Calculate health score for each module based on violations
        
        Returns:
            Dict mapping module_name -> health_score (0-100)
        """
        module_violations = {}
        
        violations = fengshui_data.get('violations', [])
        
        # Count violations per module
        for violation in violations:
            module = violation.get('module', 'unknown')
            module_violations[module] = module_violations.get(module, 0) + 1
        
        # Convert to health score (100 - violations, capped at 0)
        # Assumption: 0 violations = 100 health, 20+ violations = 0 health
        module_health = {}
        for module, violation_count in module_violations.items():
            health = max(0, 100 - (violation_count * 5))  # -5 points per violation
            module_health[module] = health
        
        return module_health
    
    def _calculate_test_health(self, guwu_data: Dict) -> Dict[str, float]:
        """
        Calculate test health for each module
        
        Returns:
            Dict mapping module_name -> test_health_score (0-100)
        """
        module_test_health = {}
        
        test_results = guwu_data.get('test_results', [])
        
        # Calculate health per module
        module_metrics = {}
        for test in test_results:
            module = test.get('module', 'unknown')
            
            if module not in module_metrics:
                module_metrics[module] = {
                    'total_tests': 0,
                    'passed_tests': 0,
                    'flaky_tests': 0
                }
            
            module_metrics[module]['total_tests'] += 1
            
            if test.get('status') == 'passed':
                module_metrics[module]['passed_tests'] += 1
            
            if test.get('is_flaky', False):
                module_metrics[module]['flaky_tests'] += 1
        
        # Convert to health score
        for module, metrics in module_metrics.items():
            if metrics['total_tests'] == 0:
                continue
            
            # Success rate contribution (70%)
            success_rate = metrics['passed_tests'] / metrics['total_tests']
            
            # Flakiness penalty (30%)
            flaky_rate = metrics['flaky_tests'] / metrics['total_tests']
            flaky_penalty = flaky_rate * 30  # Max -30 points
            
            health = (success_rate * 70) + (30 - flaky_penalty)
            module_test_health[module] = health
        
        return module_test_health
    
    def _calculate_health_correlation_confidence(
        self,
        avg_code_health: float,
        avg_test_health: float,
        affected_count: int
    ) -> float:
        """Calculate confidence for health correlation"""
        # Code health degradation (lower = more confidence)
        code_degradation = 1.0 - (avg_code_health / 100.0)
        
        # Test health degradation
        test_degradation = 1.0 - (avg_test_health / 100.0)
        
        # Pattern strength
        pattern_confidence = min(1.0, affected_count / 5.0)
        
        # Weighted combination
        confidence = (
            code_degradation * 0.4 +
            test_degradation * 0.4 +
            pattern_confidence * 0.2
        )
        
        return confidence
    
    def _explain_root_cause(
        self,
        avg_code_health: float,
        avg_test_health: float,
        count: int
    ) -> str:
        """Generate root cause explanation"""
        return f"""
{count} modules have both poor code health ({avg_code_health:.1f}/100) and poor test health ({avg_test_health:.1f}/100).

Root Cause: Technical debt accumulation creates a vicious cycle:
1. Poor code design → Hard to test properly
2. Hard to test → Tests become flaky/incomplete
3. Flaky tests → Low confidence in changes
4. Low confidence → Further code degradation

This is SYSTEMIC - not isolated issues, but module-wide quality decay.

Indicators of unhealthy modules:
- High violation count (DI, complexity, security)
- Low test success rate (<70%)
- High test flakiness (>20%)
- Developers avoid touching them ("legacy" code)

Both code and tests suffer together - they are one system, not two.
"""
    
    def _generate_recommendation(self, unhealthy_modules: list) -> str:
        """Generate actionable recommendation"""
        worst_module = min(unhealthy_modules, key=lambda m: m['code_health'])
        
        return f"""
IMMEDIATE ACTION:
1. Target worst module first: {worst_module['name']}
   - Code health: {worst_module['code_health']:.1f}/100
   - Test health: {worst_module['test_health']:.1f}/100

2. Apply "Strangler Fig" pattern:
   - Don't rewrite everything at once
   - Fix violations incrementally
   - Stabilize tests as you go
   - Measure improvement

SYSTEMATIC IMPROVEMENT:
Week 1: Fix critical violations (DI, security)
Week 2: Refactor complex code (break into smaller pieces)
Week 3: Improve test coverage and stability
Week 4: Measure new health scores

EXPECTED OUTCOME:
- Code health: {worst_module['code_health']:.1f} → 80+ (healthy)
- Test health: {worst_module['test_health']:.1f} → 80+ (stable)
- Developer confidence restored
- Module becomes maintainable again

SUCCESS METRICS:
- Violation count reduced by 50%+
- Test success rate >90%
- Test flakiness <5%
- Code review comments decrease
- Developers stop avoiding the module

PHILOSOPHY:
"You cannot fix tests without fixing code.
 You cannot fix code without fixing tests.
 They are Yin and Yang - heal them together."

Next modules to address (in order):
{chr(10).join(f"{i+1}. {m['name']} (code: {m['code_health']:.0f}, tests: {m['test_health']:.0f})" 
              for i, m in enumerate(sorted(unhealthy_modules, key=lambda x: x['code_health'])[1:4]))}
"""