"""
Unit Tests for Feng Shui Adapter

Tests the Feng Shui → Gu Wu adapter functionality.

MED-25: Feng Shui + Gu Wu Integration Bridge
"""

import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Import Feng Shui types for testing
from tools.fengshui.agents.base_agent import Finding, Severity, AgentReport
from tools.guwu.adapters import FengShuiAdapter


class TestFengShuiAdapter:
    """Test suite for FengShuiAdapter"""
    
    @pytest.fixture
    def sample_findings(self) -> List[Finding]:
        """Create sample Feng Shui findings"""
        return [
            Finding(
                category="Root Directory Clutter",
                severity=Severity.HIGH,
                file_path=Path("temp_old.py"),
                line_number=None,
                description="Unauthorized file in root directory: temp_old.py",
                recommendation="DELETE (temporary/obsolete file)",
                code_snippet=None
            ),
            Finding(
                category="Misplaced Script",
                severity=Severity.MEDIUM,
                file_path=Path("scripts/python/test_something.py"),
                line_number=None,
                description="Test script in wrong location: test_something.py",
                recommendation="Move to scripts/test/ or tests/integration/",
                code_snippet=None
            ),
            Finding(
                category="Obsolete File",
                severity=Severity.LOW,
                file_path=Path("scripts/tmp/old_script.py"),
                line_number=None,
                description="Temporary file older than 7 days: old_script.py",
                recommendation="DELETE (one-shot scripts should be short-lived)",
                code_snippet=None
            ),
            Finding(
                category="Root Directory Clutter",
                severity=Severity.CRITICAL,
                file_path=Path("check_db.py"),
                line_number=None,
                description="Utility script in root: check_db.py",
                recommendation="MOVE to scripts/test/",
                code_snippet=None
            )
        ]
    
    @pytest.fixture
    def sample_report(self, sample_findings) -> AgentReport:
        """Create sample Feng Shui agent report"""
        return AgentReport(
            agent_name="file_organization",
            module_path=Path("."),
            execution_time_seconds=1.5,
            findings=sample_findings,
            metrics={'total_findings': 4, 'critical_count': 1, 'high_count': 1},
            summary="File organization issues detected"
        )
    
    def test_adapter_initialization(self):
        """Test: Adapter initializes correctly"""
        adapter = FengShuiAdapter()
        assert adapter is not None
        assert hasattr(adapter, 'logger')
    
    def test_parse_report_basic(self, sample_report):
        """Test: Parse Feng Shui report to Gu Wu format"""
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(sample_report)
        
        assert len(findings) == 4
        assert all(isinstance(f, dict) for f in findings)
        
        # Check first finding structure
        first = findings[0]
        assert 'category' in first
        assert 'severity' in first
        assert 'file_path' in first
        assert 'description' in first
        assert 'recommendation' in first
        assert 'agent_name' in first
        assert 'module_path' in first
        
        assert first['agent_name'] == 'file_organization'
        assert first['module_path'] == Path(".")
    
    def test_parse_report_with_severity_filter(self, sample_report):
        """Test: Filter by minimum severity"""
        adapter = FengShuiAdapter()
        
        # Filter for HIGH and above (should get CRITICAL + HIGH = 2)
        findings = adapter.parse_report(sample_report, min_severity='high')
        assert len(findings) == 2
        
        severities = [f['severity'] for f in findings]
        assert 'critical' in severities
        assert 'high' in severities
        assert 'medium' not in severities
        assert 'low' not in severities
    
    def test_parse_report_with_category_filter(self, sample_report):
        """Test: Filter by category"""
        adapter = FengShuiAdapter()
        
        # Filter for specific category
        findings = adapter.parse_report(
            sample_report,
            categories=['Root Directory Clutter']
        )
        
        assert len(findings) == 2  # 2 findings in this category
        assert all(f['category'] == 'Root Directory Clutter' for f in findings)
    
    def test_parse_report_combined_filters(self, sample_report):
        """Test: Apply both severity and category filters"""
        adapter = FengShuiAdapter()
        
        findings = adapter.parse_report(
            sample_report,
            min_severity='high',
            categories=['Root Directory Clutter']
        )
        
        # Should get only CRITICAL + HIGH findings from this category
        assert len(findings) == 2
        assert all(f['category'] == 'Root Directory Clutter' for f in findings)
        
        severities = [f['severity'] for f in findings]
        assert 'critical' in severities
        assert 'high' in severities
    
    def test_filter_by_category(self, sample_report):
        """Test: Post-parse category filtering"""
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(sample_report)
        
        filtered = adapter.filter_by_category(findings, 'Misplaced Script')
        
        assert len(filtered) == 1
        assert filtered[0]['category'] == 'Misplaced Script'
    
    def test_filter_by_severity(self, sample_report):
        """Test: Post-parse severity filtering"""
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(sample_report)
        
        # Filter for MEDIUM and above
        filtered = adapter.filter_by_severity(findings, min_severity='medium')
        
        assert len(filtered) == 3  # CRITICAL + HIGH + MEDIUM
        severities = [f['severity'] for f in filtered]
        assert 'low' not in severities
    
    def test_group_by_category(self, sample_report):
        """Test: Group findings by category"""
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(sample_report)
        
        grouped = adapter.group_by_category(findings)
        
        assert len(grouped) == 3  # 3 categories
        assert 'Root Directory Clutter' in grouped
        assert 'Misplaced Script' in grouped
        assert 'Obsolete File' in grouped
        
        # Check counts
        assert len(grouped['Root Directory Clutter']) == 2
        assert len(grouped['Misplaced Script']) == 1
        assert len(grouped['Obsolete File']) == 1
    
    def test_get_summary(self, sample_report):
        """Test: Get summary statistics"""
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(sample_report)
        
        summary = adapter.get_summary(findings)
        
        assert summary['total'] == 4
        assert summary['critical'] == 1
        assert summary['high'] == 1
        assert summary['medium'] == 1
        assert summary['low'] == 1
    
    def test_enhanced_fields_preserved(self):
        """Test: Enhanced fields (v4.34+) are preserved"""
        # Create finding with enhanced fields
        finding = Finding(
            category="Test Category",
            severity=Severity.HIGH,
            file_path=Path("test.py"),
            line_number=10,
            description="Test issue",
            recommendation="Fix it",
            code_snippet="x = 1",
            code_snippet_with_context="9: # comment\n10: x = 1\n11: y = 2",
            issue_explanation="This is why it's bad",
            fix_example="x = 2  # Better",
            impact_estimate="10-20% speedup",
            effort_estimate="30 min"
        )
        
        report = AgentReport(
            agent_name="test",
            module_path=Path("."),
            execution_time_seconds=1.0,
            findings=[finding]
        )
        
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(report)
        
        assert len(findings) == 1
        f = findings[0]
        
        # Check enhanced fields
        assert f['code_snippet_with_context'] == "9: # comment\n10: x = 1\n11: y = 2"
        assert f['issue_explanation'] == "This is why it's bad"
        assert f['fix_example'] == "x = 2  # Better"
        assert f['impact_estimate'] == "10-20% speedup"
        assert f['effort_estimate'] == "30 min"
    
    def test_gof_pattern_fields_preserved(self):
        """Test: GoF pattern fields (v4.36+) are preserved"""
        finding = Finding(
            category="DI Violation",
            severity=Severity.HIGH,
            file_path=Path("service.py"),
            line_number=15,
            description="Direct instantiation",
            recommendation="Use Dependency Injection",
            gof_pattern_suggestion="Factory Pattern",
            gof_pattern_rationale="Encapsulate object creation",
            gof_pattern_example="factory = ServiceFactory()\nservice = factory.create()"
        )
        
        report = AgentReport(
            agent_name="architect",
            module_path=Path("."),
            execution_time_seconds=1.0,
            findings=[finding]
        )
        
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(report)
        
        assert len(findings) == 1
        f = findings[0]
        
        # Check GoF fields
        assert f['gof_pattern_suggestion'] == "Factory Pattern"
        assert f['gof_pattern_rationale'] == "Encapsulate object creation"
        assert f['gof_pattern_example'] == "factory = ServiceFactory()\nservice = factory.create()"
    
    def test_empty_report(self):
        """Test: Handle empty report"""
        report = AgentReport(
            agent_name="test",
            module_path=Path("."),
            execution_time_seconds=0.5,
            findings=[],
            summary="No issues found"
        )
        
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(report)
        
        assert len(findings) == 0
        assert isinstance(findings, list)
    
    def test_invalid_severity_filter(self, sample_report):
        """Test: Invalid severity filter defaults to 'low'"""
        adapter = FengShuiAdapter()
        
        # Should not crash, should use default
        findings = adapter.parse_report(sample_report, min_severity='invalid')
        
        # Should include all findings (defaults to 'low')
        assert len(findings) == 4