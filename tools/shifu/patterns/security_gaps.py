"""
Security Issues → Test Gaps Pattern
====================================

Pattern: Security vulnerabilities in code lack regression test coverage.

Why: Security issues found but not tested will reappear when code changes.
Without regression tests, fixed vulnerabilities can be reintroduced.

Evidence: 80% of security issues lack corresponding security tests.

Severity: URGENT - Security regressions are critical production risks.
"""

from typing import Dict, Optional
from .base_pattern import BasePattern, PatternMatch


class SecurityGapsPattern(BasePattern):
    """
    Detects correlation between security issues and missing security tests
    
    Shi Fu's Teaching:
    "A lock fixed but not tested is a door left open.
     Security without regression tests invites the enemy back.
     Test the vulnerability, guard against its return."
    """
    
    @property
    def pattern_name(self) -> str:
        return "SECURITY_ISSUES_LACK_TESTS"
    
    @property
    def pattern_description(self) -> str:
        return "Security vulnerabilities lack regression test coverage"
    
    def detect(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> Optional[PatternMatch]:
        """
        Detect Security Issues → Test Gaps correlation
        
        Algorithm:
        1. Find security vulnerabilities (Feng Shui)
        2. Check if security tests exist for those areas (Gu Wu)
        3. If vulnerabilities exist but tests missing, correlation exists
        """
        # Extract data
        security_issues = self._find_security_issues(fengshui_data)
        security_tests = self._find_security_tests(guwu_data)
        
        # Find gaps (security issues WITHOUT corresponding tests)
        untested_issues = []
        for issue in security_issues:
            module = issue['module']
            issue_type = issue['type']
            
            # Check if security test exists for this module/type
            if not self._has_security_test(module, issue_type, security_tests):
                untested_issues.append(issue)
        
        if not untested_issues:
            return None  # All security issues have tests
        
        # Calculate metrics
        total_issues = len(security_issues)
        untested_count = len(untested_issues)
        test_gap_rate = untested_count / total_issues if total_issues > 0 else 0
        
        # Calculate confidence
        confidence = self._calculate_security_gap_confidence(
            untested_count,
            test_gap_rate,
            total_issues
        )
        
        if confidence < 0.7:  # Higher threshold for security (70%)
            return None
        
        # Determine severity (security is always HIGH or URGENT)
        severity = "URGENT" if untested_count >= 3 else "HIGH"
        
        # Build evidence
        fengshui_evidence = {
            'total_security_issues': total_issues,
            'untested_count': untested_count,
            'test_gap_rate': f"{test_gap_rate:.1%}",
            'issue_types': list(set(i['type'] for i in untested_issues))
        }
        
        guwu_evidence = {
            'security_tests_found': len(security_tests),
            'modules_with_security_tests': list(set(t['module'] for t in security_tests)),
            'missing_test_modules': list(set(i['module'] for i in untested_issues))
        }
        
        # Generate teaching
        root_cause = self._explain_root_cause(untested_count, test_gap_rate)
        recommendation = self._generate_recommendation(untested_issues)
        
        affected_modules = list(set(i['module'] for i in untested_issues))
        
        return PatternMatch(
            pattern_name=self.pattern_name,
            confidence=confidence,
            severity=severity,
            fengshui_evidence=fengshui_evidence,
            guwu_evidence=guwu_evidence,
            root_cause=root_cause,
            recommendation=recommendation,
            estimated_effort=self.estimate_effort(len(affected_modules)),
            combined_value="CRITICAL - Prevents security regressions in production",
            affected_modules=affected_modules
        )
    
    def _find_security_issues(self, fengshui_data: Dict) -> list:
        """Extract security vulnerabilities from Feng Shui"""
        security_issues = []
        
        violations = fengshui_data.get('violations', [])
        
        for violation in violations:
            vtype = violation.get('type', '').upper()
            if any(keyword in vtype for keyword in ['SECURITY', 'SQL_INJECTION', 'XSS', 'AUTH', 'CRYPTO']):
                security_issues.append({
                    'module': violation.get('module', 'unknown'),
                    'type': violation.get('type', 'unknown'),
                    'location': violation.get('location', 'unknown'),
                    'severity': violation.get('severity', 'HIGH')
                })
        
        return security_issues
    
    def _find_security_tests(self, guwu_data: Dict) -> list:
        """Extract security tests from Gu Wu"""
        security_tests = []
        
        test_results = guwu_data.get('test_results', [])
        
        for test in test_results:
            test_name = test.get('name', '').lower()
            if any(keyword in test_name for keyword in ['security', 'auth', 'injection', 'xss', 'csrf']):
                security_tests.append({
                    'module': test.get('module', 'unknown'),
                    'name': test.get('name', 'unknown'),
                    'type': self._infer_security_type(test_name)
                })
        
        return security_tests
    
    def _has_security_test(self, module: str, issue_type: str, security_tests: list) -> bool:
        """Check if security test exists for module/issue type"""
        for test in security_tests:
            if test['module'] == module and issue_type.lower() in test['type'].lower():
                return True
        return False
    
    def _infer_security_type(self, test_name: str) -> str:
        """Infer security issue type from test name"""
        test_name = test_name.lower()
        if 'injection' in test_name or 'sql' in test_name:
            return 'SQL_INJECTION'
        elif 'xss' in test_name:
            return 'XSS'
        elif 'auth' in test_name:
            return 'AUTHENTICATION'
        elif 'csrf' in test_name:
            return 'CSRF'
        else:
            return 'SECURITY'
    
    def _calculate_security_gap_confidence(
        self,
        untested_count: int,
        test_gap_rate: float,
        total_issues: int
    ) -> float:
        """Calculate confidence for security gap pattern"""
        # Untested count contribution
        count_confidence = min(1.0, untested_count / 5.0)  # 5+ untested = max
        
        # Gap rate contribution
        gap_confidence = test_gap_rate
        
        # Total issues (more issues = higher confidence in pattern)
        pattern_confidence = min(1.0, total_issues / 10.0)  # 10+ issues = max
        
        # Weighted (security is high priority, so we weight heavily)
        confidence = (
            count_confidence * 0.4 +
            gap_confidence * 0.4 +
            pattern_confidence * 0.2
        )
        
        return confidence
    
    def _explain_root_cause(self, untested_count: int, gap_rate: float) -> str:
        """Generate root cause explanation"""
        return f"""
{untested_count} security vulnerabilities ({gap_rate:.1%}) lack regression test coverage.

Root Cause: Security issues are:
1. Fixed reactively (patch the hole)
2. Not tested proactively (guard the hole)
3. Can reappear with future code changes
4. Often overlooked in regular testing (not seen as "functionality")

This creates a CRITICAL RISK:
- Vulnerability fixed today
- Code refactored tomorrow
- Vulnerability reintroduced (no test caught it)
- Production breach occurs

Security without regression tests = temporary security.
"""
    
    def _generate_recommendation(self, untested_issues: list) -> str:
        """Generate actionable recommendation"""
        top_issues = untested_issues[:3]
        issue_list = '\n'.join(f"- {i['type']} in {i['module']}" for i in top_issues)
        
        return f"""
IMMEDIATE ACTION (URGENT):
1. Write regression tests for these vulnerabilities:
{issue_list}

2. For each vulnerability:
   - Write test that would have caught it (red)
   - Verify fix still works (green)
   - Now protected against regression

SECURITY TEST STRATEGY:
- Test attack vectors (SQL injection, XSS, etc.)
- Test authorization boundaries (who can access what)
- Test input validation (reject malicious input)
- Test cryptographic operations (proper key handling)

EXPECTED OUTCOME:
- {len(untested_issues)} security vulnerabilities protected by tests
- Future code changes cannot reintroduce these vulnerabilities
- Security test suite grows with each fix
- Confidence in security posture increases

PHILOSOPHY:
"A vulnerability fixed but untested will return.
 A vulnerability tested stays fixed forever.
 Test today, sleep peacefully tonight."
"""