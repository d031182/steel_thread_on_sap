"""
High Complexity → Low Coverage Pattern
=======================================

Pattern: Functions/modules with high cyclomatic complexity have low test coverage.

Why: Complex code has many execution paths, making it harder to test thoroughly.
Developers often skip comprehensive testing of complex code due to effort required.

Evidence: Functions with complexity >10 typically have <50% coverage.

Severity: HIGH - Complex untested code is high-risk for bugs.
"""

from typing import Dict, Optional
from .base_pattern import BasePattern, PatternMatch


class ComplexityCoveragePattern(BasePattern):
    """
    Detects correlation between code complexity and test coverage gaps
    
    Shi Fu's Teaching:
    "Complexity is like a maze - many paths, easy to get lost.
     When code is complex, testing becomes burdensome.
     Simplify first, then testing becomes natural."
    """
    
    @property
    def pattern_name(self) -> str:
        return "COMPLEXITY_CAUSES_LOW_COVERAGE"
    
    @property
    def pattern_description(self) -> str:
        return "High cyclomatic complexity correlates with low test coverage"
    
    def detect(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> Optional[PatternMatch]:
        """
        Detect Complexity → Low Coverage correlation
        
        Algorithm:
        1. Find functions/modules with high complexity (Feng Shui)
        2. Check coverage for same code units (Gu Wu)
        3. If complexity high AND coverage low, correlation exists
        """
        # Extract data
        complex_units = self._find_complex_code_units(fengshui_data)
        coverage_data = self._extract_coverage_data(guwu_data)
        
        # Find correlation
        affected_units = []
        for unit_name, complexity in complex_units.items():
            coverage = coverage_data.get(unit_name, 1.0)  # Default 100% if not found
            
            # Pattern: complexity >10 AND coverage <50%
            if complexity > 10 and coverage < 0.5:
                affected_units.append({
                    'name': unit_name,
                    'complexity': complexity,
                    'coverage': coverage
                })
        
        if not affected_units:
            return None  # No correlation
        
        # Calculate metrics
        avg_complexity = sum(u['complexity'] for u in affected_units) / len(affected_units)
        avg_coverage = sum(u['coverage'] for u in affected_units) / len(affected_units)
        
        # Calculate confidence
        confidence = self._calculate_complexity_coverage_confidence(
            avg_complexity,
            avg_coverage,
            len(affected_units)
        )
        
        if confidence < 0.6:
            return None
        
        # Determine severity
        impact_score = (avg_complexity / 20.0) * (1.0 - avg_coverage)  # Max complexity ~20
        severity = self.determine_severity(impact_score, len(affected_units))
        
        # Build evidence
        fengshui_evidence = {
            'average_complexity': f"{avg_complexity:.1f}",
            'affected_units': [u['name'] for u in affected_units[:5]],  # Top 5
            'complexity_details': {u['name']: u['complexity'] for u in affected_units[:5]}
        }
        
        guwu_evidence = {
            'average_coverage': f"{avg_coverage:.1%}",
            'affected_units': [u['name'] for u in affected_units[:5]],
            'coverage_details': {u['name']: f"{u['coverage']:.1%}" for u in affected_units[:5]}
        }
        
        # Generate teaching
        root_cause = self._explain_root_cause(avg_complexity, avg_coverage, len(affected_units))
        recommendation = self._generate_recommendation(affected_units)
        
        return PatternMatch(
            pattern_name=self.pattern_name,
            confidence=confidence,
            severity=severity,
            fengshui_evidence=fengshui_evidence,
            guwu_evidence=guwu_evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            estimated_effort=self.estimate_effort(len(affected_units)),
            combined_value="High - Simplifying code makes testing easier, improves both",
            affected_modules=[u['name'].split('.')[0] for u in affected_units]
        )
    
    def _find_complex_code_units(self, fengshui_data: Dict) -> Dict[str, int]:
        """
        Extract code units with high complexity
        
        Returns:
            Dict mapping unit_name -> complexity_score
        """
        complex_units = {}
        
        # Extract from Feng Shui complexity metrics
        complexity_violations = fengshui_data.get('violations', [])
        
        for violation in complexity_violations:
            if 'COMPLEXITY' in violation.get('type', '').upper():
                unit_name = violation.get('location', 'unknown')
                complexity = violation.get('complexity_score', 0)
                
                # Pattern threshold: complexity >10
                if complexity > 10:
                    complex_units[unit_name] = complexity
        
        return complex_units
    
    def _extract_coverage_data(self, guwu_data: Dict) -> Dict[str, float]:
        """
        Extract test coverage data
        
        Returns:
            Dict mapping unit_name -> coverage_percentage (0.0-1.0)
        """
        coverage_map = {}
        
        # Extract from Gu Wu coverage metrics
        coverage_results = guwu_data.get('coverage', {})
        
        for unit_name, metrics in coverage_results.items():
            coverage_pct = metrics.get('line_coverage', 1.0)  # Default 100%
            coverage_map[unit_name] = coverage_pct
        
        return coverage_map
    
    def _calculate_complexity_coverage_confidence(
        self,
        avg_complexity: float,
        avg_coverage: float,
        affected_count: int
    ) -> float:
        """
        Calculate confidence that complexity CAUSES low coverage
        
        Confidence factors:
        - Higher complexity = higher confidence
        - Lower coverage = higher confidence
        - More affected units = higher confidence (pattern, not isolated)
        """
        # Complexity contribution (normalize to 0-1, max at 20)
        complexity_confidence = min(1.0, avg_complexity / 20.0)
        
        # Coverage gap contribution (invert: low coverage = high confidence)
        coverage_gap_confidence = 1.0 - avg_coverage
        
        # Pattern strength
        pattern_confidence = min(1.0, affected_count / 10.0)  # 10+ units = max
        
        # Weighted combination
        confidence = (
            complexity_confidence * 0.4 +
            coverage_gap_confidence * 0.4 +
            pattern_confidence * 0.2
        )
        
        return confidence
    
    def _explain_root_cause(
        self,
        avg_complexity: float,
        avg_coverage: float,
        count: int
    ) -> str:
        """Generate root cause explanation"""
        return f"""
{count} code units have high complexity (avg: {avg_complexity:.1f}) with low test coverage (avg: {avg_coverage:.1%}).

Root Cause: Complex code with many branches/paths is:
1. Harder to understand (cognitive load)
2. Tedious to test comprehensively (many test cases needed)
3. Often skipped or partially tested (developer fatigue)
4. High-risk for bugs (untested paths fail in production)

This is NOT a testing problem - it's a CODE DESIGN problem.
Simplify the code first, testing becomes easier naturally.
"""
    
    def _generate_recommendation(self, affected_units: list) -> str:
        """Generate actionable recommendation"""
        top_unit = affected_units[0]['name'] if affected_units else 'unknown'
        top_complexity = affected_units[0]['complexity'] if affected_units else 0
        
        return f"""
IMMEDIATE ACTION:
1. Refactor high-complexity units (start with: {top_unit}, complexity: {top_complexity})
2. Break complex functions into smaller, single-purpose functions
3. Tests will become easier to write automatically

REFACTORING STRATEGY:
- Extract Method: Break long functions into focused helpers
- Replace Conditional with Polymorphism: Use strategy pattern for complex if/else
- Simplify Boolean Expressions: Extract conditions to named methods
- Reduce Nesting: Early returns, guard clauses

EXPECTED OUTCOME:
- Complexity drops from {affected_units[0]['complexity']:.0f} to <10
- Coverage rises from {affected_units[0]['coverage']:.1%} to 70%+
- Code becomes self-documenting (smaller, focused functions)
- Bug surface area reduced (fewer paths to fail)

PHILOSOPHY:
"The master does not fight complexity with more tests.
 The master removes complexity, then tests write themselves."
"""