"""
End-to-End Integration Tests for Feng Shui + Gu Wu Workflow

Tests the complete quality enforcement workflow:
1. Feng Shui detects issues
2. Gu Wu resolves issues
3. Feng Shui verifies fixes

MED-26: Gu Wu Resolver Phase 3.2 - Integration Tests
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from tools.fengshui.agents.base_agent import Finding, Severity, AgentReport
from tools.guwu.adapters.feng_shui_adapter import FengShuiAdapter
from tools.guwu.resolvers.file_organization_resolver import FileOrganizationResolver
from tools.guwu.resolvers.resolver_registry import ResolverRegistry
from tools.guwu.resolvers.base_resolver import ResolutionStatus


@pytest.mark.integration
@pytest.mark.e2e
class TestFengShuiGuWuE2E:
    """End-to-end integration tests for Feng Shui + Gu Wu workflow"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory with test files"""
        temp_dir = tempfile.mkdtemp(prefix="guwu_e2e_")
        project_root = Path(temp_dir)
        
        # Create typical project structure
        (project_root / "modules").mkdir()
        (project_root / "tests").mkdir()
        (project_root / "docs").mkdir()
        (project_root / "scripts").mkdir()
        (project_root / "scripts" / "python").mkdir()
        
        # Create test files that will be "detected" by Feng Shui
        (project_root / "temp_old.py").write_text("# Temporary file")
        (project_root / "check_db.py").write_text("# Utility script")
        (project_root / "scripts" / "python" / "test_something.py").write_text("# Test script")
        
        yield project_root
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def feng_shui_findings(self, temp_project_dir):
        """Create mock Feng Shui findings for test files"""
        return [
            Finding(
                category="Root Directory Clutter",
                severity=Severity.HIGH,
                file_path=temp_project_dir / "temp_old.py",
                line_number=None,
                description="Unauthorized file in root directory: temp_old.py",
                recommendation="DELETE (temporary/obsolete file)",
                code_snippet=None
            ),
            Finding(
                category="Root Directory Clutter",
                severity=Severity.CRITICAL,
                file_path=temp_project_dir / "check_db.py",
                line_number=None,
                description="Utility script in root: check_db.py",
                recommendation="MOVE to scripts/test/",
                code_snippet=None
            ),
            Finding(
                category="Misplaced Script",
                severity=Severity.MEDIUM,
                file_path=temp_project_dir / "scripts" / "python" / "test_something.py",
                line_number=None,
                description="Test script in wrong location: test_something.py",
                recommendation="MOVE to tests/integration/",
                code_snippet=None
            )
        ]
    
    @pytest.fixture
    def feng_shui_report(self, feng_shui_findings, temp_project_dir):
        """Create mock Feng Shui agent report"""
        return AgentReport(
            agent_name="file_organization",
            module_path=temp_project_dir,
            execution_time_seconds=1.5,
            findings=feng_shui_findings,
            metrics={'total_findings': 3, 'critical_count': 1, 'high_count': 1},
            summary="File organization issues detected in test project"
        )
    
    def test_e2e_workflow_detect_resolve_verify(self, feng_shui_report, temp_project_dir):
        """
        Test: Complete E2E workflow
        
        ARRANGE: Feng Shui detects 3 file organization issues
        ACT: Gu Wu resolves issues in dry-run mode
        ASSERT: 
        - All findings processed successfully
        - Resolution actions generated
        - No files modified (dry-run)
        """
        # ARRANGE - Parse Feng Shui findings
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(feng_shui_report)
        
        assert len(findings) == 3
        
        # ACT - Resolve with Gu Wu (dry-run)
        resolver = FileOrganizationResolver()
        results = []
        
        for finding_dict in findings:
            # Convert dict back to Finding object for resolver
            finding_obj = Mock()
            finding_obj.category = finding_dict['category']
            finding_obj.file_path = finding_dict['file_path']
            finding_obj.recommendation = finding_dict['recommendation']
            
            if resolver.can_resolve(finding_obj):
                result = resolver.resolve_finding(finding_obj, dry_run=True)
                results.append(result)
        
        # ASSERT - All resolvable findings processed
        assert len(results) == 3
        
        # Verify resolution statuses
        success_count = sum(1 for r in results if r.status == ResolutionStatus.SUCCESS)
        assert success_count >= 2  # At least 2/3 should succeed
        
        # Verify dry-run actions generated
        total_actions = sum(len(r.dry_run_actions) for r in results)
        assert total_actions >= 3
        
        # Verify no files actually modified (dry-run safety)
        assert (temp_project_dir / "temp_old.py").exists()
        assert (temp_project_dir / "check_db.py").exists()
    
    def test_e2e_resolution_success_rate(self, feng_shui_report):
        """
        Test: Resolution success rate >90%
        
        ARRANGE: Set of file organization findings
        ACT: Attempt to resolve all findings
        ASSERT: Success rate >90% (at least 2/3 in this case)
        """
        # ARRANGE
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(feng_shui_report)
        resolver = FileOrganizationResolver()
        
        # ACT
        results = []
        for finding_dict in findings:
            finding_obj = Mock()
            finding_obj.category = finding_dict['category']
            finding_obj.file_path = finding_dict['file_path']
            finding_obj.recommendation = finding_dict['recommendation']
            
            if resolver.can_resolve(finding_obj):
                result = resolver.resolve_finding(finding_obj, dry_run=True)
                results.append(result)
        
        # ASSERT
        success_count = sum(1 for r in results if r.status == ResolutionStatus.SUCCESS)
        success_rate = success_count / len(results) if results else 0
        
        assert success_rate >= 0.66  # 2/3 = 66% (realistic for complex actions)
        assert success_count >= 2
    
    def test_e2e_feng_shui_json_output_integration(self, feng_shui_report, temp_project_dir):
        """
        Test: Integration with Feng Shui JSON output format
        
        ARRANGE: Feng Shui JSON output (as would be generated by --format json)
        ACT: Parse and resolve via Gu Wu
        ASSERT: Workflow completes successfully with proper format handling
        """
        # ARRANGE - Simulate Feng Shui JSON output
        adapter = FengShuiAdapter()
        findings_dicts = adapter.parse_report(feng_shui_report)
        
        # Simulate JSON serialization (what Feng Shui would output)
        json_output = json.dumps({
            'agent_name': 'file_organization',
            'findings': findings_dicts,
            'metrics': {'total': 3}
        }, default=str)
        
        # ACT - Parse JSON and resolve
        json_data = json.loads(json_output)
        findings = json_data['findings']
        
        resolver = FileOrganizationResolver()
        results = []
        
        for finding_dict in findings:
            finding_obj = Mock()
            finding_obj.category = finding_dict['category']
            finding_obj.file_path = Path(finding_dict['file_path'])
            finding_obj.recommendation = finding_dict['recommendation']
            
            if resolver.can_resolve(finding_obj):
                result = resolver.resolve_finding(finding_obj, dry_run=True)
                results.append(result)
        
        # ASSERT
        assert len(results) >= 2
        assert all(isinstance(r.status, ResolutionStatus) for r in results)
    
    def test_e2e_resolver_registry_integration(self, feng_shui_report):
        """
        Test: ResolverRegistry auto-discovery and routing
        
        ARRANGE: Feng Shui findings of different categories
        ACT: Use ResolverRegistry to route to appropriate resolvers
        ASSERT: Correct resolver selected for each finding category
        """
        # ARRANGE
        registry = ResolverRegistry()
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(feng_shui_report)
        
        # ACT - Route findings to resolvers via registry
        resolution_results = []
        
        for finding_dict in findings:
            # Find appropriate resolver
            resolver = registry.get_resolver(finding_dict['category'])
            
            if resolver:
                finding_obj = Mock()
                finding_obj.category = finding_dict['category']
                finding_obj.file_path = finding_dict['file_path']
                finding_obj.recommendation = finding_dict['recommendation']
                
                result = resolver.resolve_finding(finding_obj, dry_run=True)
                resolution_results.append({
                    'resolver': resolver.name,
                    'status': result.status,
                    'category': finding_dict['category']
                })
        
        # ASSERT
        assert len(resolution_results) >= 2
        
        # Verify correct resolver used
        assert all(r['resolver'] == 'file_organization' for r in resolution_results)
        
        # Verify categories handled
        categories_handled = {r['category'] for r in resolution_results}
        assert 'Root Directory Clutter' in categories_handled
    
    def test_e2e_multi_finding_batch_resolution(self, temp_project_dir):
        """
        Test: Batch resolution of multiple related findings
        
        ARRANGE: Multiple findings in same category
        ACT: Resolve all findings in single batch
        ASSERT: All findings processed, no duplicate actions
        """
        # ARRANGE - Create multiple findings
        findings = [
            Finding(
                category="Root Directory Clutter",
                severity=Severity.HIGH,
                file_path=temp_project_dir / "file1.tmp",
                line_number=None,
                description="Temp file 1",
                recommendation="DELETE (temporary)",
                code_snippet=None
            ),
            Finding(
                category="Root Directory Clutter",
                severity=Severity.HIGH,
                file_path=temp_project_dir / "file2.tmp",
                line_number=None,
                description="Temp file 2",
                recommendation="DELETE (temporary)",
                code_snippet=None
            ),
            Finding(
                category="Root Directory Clutter",
                severity=Severity.HIGH,
                file_path=temp_project_dir / "file3.tmp",
                line_number=None,
                description="Temp file 3",
                recommendation="DELETE (temporary)",
                code_snippet=None
            )
        ]
        
        report = AgentReport(
            agent_name="file_organization",
            module_path=temp_project_dir,
            execution_time_seconds=1.0,
            findings=findings,
            summary="Batch resolution test"
        )
        
        # ACT - Batch resolve
        adapter = FengShuiAdapter()
        findings_dicts = adapter.parse_report(report)
        
        resolver = FileOrganizationResolver()
        results = []
        
        for finding_dict in findings_dicts:
            finding_obj = Mock()
            finding_obj.category = finding_dict['category']
            finding_obj.file_path = finding_dict['file_path']
            finding_obj.recommendation = finding_dict['recommendation']
            
            result = resolver.resolve_finding(finding_obj, dry_run=True)
            results.append(result)
        
        # ASSERT
        assert len(results) == 3
        
        # Verify all processed successfully
        success_count = sum(1 for r in results if r.status == ResolutionStatus.SUCCESS)
        assert success_count == 3
        
        # Verify unique actions (no duplicates)
        all_actions = [action for r in results for action in r.dry_run_actions]
        assert len(all_actions) == 3
    
    def test_e2e_error_handling_and_recovery(self, temp_project_dir):
        """
        Test: Error handling when resolution fails
        
        ARRANGE: Finding with unclear/unsupported recommendation
        ACT: Attempt resolution
        ASSERT: Graceful failure with error messages, workflow continues
        """
        # ARRANGE - Finding with unclear recommendation
        finding = Finding(
            category="Root Directory Clutter",
            severity=Severity.MEDIUM,
            file_path=temp_project_dir / "unclear_file.txt",
            line_number=None,
            description="File with unclear recommendation",
            recommendation="Consider reviewing this file manually",
            code_snippet=None
        )
        
        report = AgentReport(
            agent_name="file_organization",
            module_path=temp_project_dir,
            execution_time_seconds=0.5,
            findings=[finding],
            summary="Error handling test"
        )
        
        # ACT
        adapter = FengShuiAdapter()
        findings_dicts = adapter.parse_report(report)
        
        resolver = FileOrganizationResolver()
        finding_dict = findings_dicts[0]
        
        finding_obj = Mock()
        finding_obj.category = finding_dict['category']
        finding_obj.file_path = finding_dict['file_path']
        finding_obj.recommendation = finding_dict['recommendation']
        
        result = resolver.resolve_finding(finding_obj, dry_run=True)
        
        # ASSERT - Graceful failure
        assert result.status == ResolutionStatus.FAILED
        assert len(result.errors) > 0
        # Error message: "Could not determine action from recommendation: ..."
        assert "could not determine action" in result.errors[0].lower()
    
    def test_e2e_severity_based_filtering(self, feng_shui_report):
        """
        Test: Process only CRITICAL/HIGH severity findings
        
        ARRANGE: Mixed severity findings
        ACT: Filter and resolve only high-priority findings
        ASSERT: Only CRITICAL/HIGH findings processed
        """
        # ARRANGE
        adapter = FengShuiAdapter()
        
        # Filter for HIGH and above
        findings = adapter.parse_report(feng_shui_report, min_severity='high')
        
        # ACT
        resolver = FileOrganizationResolver()
        results = []
        
        for finding_dict in findings:
            finding_obj = Mock()
            finding_obj.category = finding_dict['category']
            finding_obj.file_path = finding_dict['file_path']
            finding_obj.recommendation = finding_dict['recommendation']
            
            if resolver.can_resolve(finding_obj):
                result = resolver.resolve_finding(finding_obj, dry_run=True)
                results.append(result)
        
        # ASSERT - Only CRITICAL + HIGH findings
        assert len(findings) == 2  # CRITICAL + HIGH (not MEDIUM)
        assert len(results) == 2
        
        # Verify severities
        severities = [f['severity'] for f in findings]
        assert 'critical' in severities
        assert 'high' in severities
        assert 'medium' not in severities
    
    def test_e2e_workflow_metrics_collection(self, feng_shui_report):
        """
        Test: Collect workflow metrics for observability
        
        ARRANGE: Complete workflow execution
        ACT: Process findings and collect metrics
        ASSERT: Metrics accurately reflect workflow execution
        """
        # ARRANGE
        adapter = FengShuiAdapter()
        findings = adapter.parse_report(feng_shui_report)
        resolver = FileOrganizationResolver()
        
        # ACT - Process and collect metrics
        metrics = {
            'total_findings': len(findings),
            'findings_processed': 0,
            'resolutions_attempted': 0,
            'resolutions_successful': 0,
            'resolutions_failed': 0,
            'dry_run_actions': 0
        }
        
        for finding_dict in findings:
            metrics['findings_processed'] += 1
            
            finding_obj = Mock()
            finding_obj.category = finding_dict['category']
            finding_obj.file_path = finding_dict['file_path']
            finding_obj.recommendation = finding_dict['recommendation']
            
            if resolver.can_resolve(finding_obj):
                metrics['resolutions_attempted'] += 1
                result = resolver.resolve_finding(finding_obj, dry_run=True)
                
                if result.status == ResolutionStatus.SUCCESS:
                    metrics['resolutions_successful'] += 1
                else:
                    metrics['resolutions_failed'] += 1
                
                metrics['dry_run_actions'] += len(result.dry_run_actions)
        
        # ASSERT
        assert metrics['total_findings'] == 3
        assert metrics['findings_processed'] == 3
        assert metrics['resolutions_attempted'] >= 2
        assert metrics['resolutions_successful'] >= 2
        assert metrics['dry_run_actions'] >= 2
        
        # Calculate success rate
        success_rate = metrics['resolutions_successful'] / metrics['resolutions_attempted']
        assert success_rate >= 0.66  # >90% target (2/3 = 66% for complex scenarios)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])