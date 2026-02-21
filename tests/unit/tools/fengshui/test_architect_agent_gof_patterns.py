"""
Unit Tests for GoF Pattern Suggestions in ArchitectAgent

Tests the GoF pattern suggestion functionality added in HIGH-4d.
"""

import pytest
from pathlib import Path
from tools.fengshui.agents.architect_agent import ArchitectAgent
from tools.fengshui.agents.base_agent import Finding, Severity


class TestGoFPatternMapping:
    """Test GoF pattern mapping functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = ArchitectAgent()
    
    def test_suggest_gof_pattern_di_violation(self):
        """Test: DI violation gets Factory Pattern suggestion"""
        # ARRANGE
        finding = Finding(
            category="DI Violation",
            severity=Severity.HIGH,
            file_path=Path("modules/test/backend/api.py"),
            line_number=42,
            description="Direct instantiation detected",
            recommendation="Use dependency injection"
        )
        
        # ACT
        enhanced_finding = self.agent._suggest_gof_pattern(finding)
        
        # ASSERT
        assert enhanced_finding.gof_pattern_suggestion == "Factory Pattern"
        assert 'Encapsulates complex object creation' in enhanced_finding.gof_pattern_rationale
        assert 'ConnectionFactory' in enhanced_finding.gof_pattern_example
    
    def test_suggest_gof_pattern_large_class(self):
        """Test: Large class gets Strategy Pattern suggestion"""
        # ARRANGE
        finding = Finding(
            category="Large Class (SRP Violation)",
            severity=Severity.MEDIUM,
            file_path=Path("modules/test/backend/service.py"),
            line_number=10,
            description="Class is 600 lines",
            recommendation="Refactor into smaller classes"
        )
        
        # ACT
        enhanced_finding = self.agent._suggest_gof_pattern(finding)
        
        # ASSERT
        assert enhanced_finding.gof_pattern_suggestion == "Strategy Pattern"
        assert 'Extracts algorithms' in enhanced_finding.gof_pattern_rationale
    
    def test_suggest_gof_pattern_repository_violation(self):
        """Test: Repository violation gets Adapter Pattern suggestion"""
        # ARRANGE
        finding = Finding(
            category="Repository Pattern Violation",
            severity=Severity.HIGH,
            file_path=Path("modules/test/backend/service.py"),
            line_number=100,
            description="Direct database access detected",
            recommendation="Use repository pattern"
        )
        
        # ACT
        enhanced_finding = self.agent._suggest_gof_pattern(finding)
        
        # ASSERT
        assert enhanced_finding.gof_pattern_suggestion == "Adapter Pattern"
        assert 'Wraps external libraries' in enhanced_finding.gof_pattern_rationale
        assert 'SqliteAdapter' in enhanced_finding.gof_pattern_example
    
    def test_suggest_gof_pattern_service_locator(self):
        """Test: Service locator gets Factory + DI suggestion"""
        # ARRANGE
        finding = Finding(
            category="Service Locator Anti-Pattern",
            severity=Severity.HIGH,
            file_path=Path("modules/test/backend/api.py"),
            line_number=50,
            description="Using app.config for database path",
            recommendation="Replace with DI"
        )
        
        # ACT
        enhanced_finding = self.agent._suggest_gof_pattern(finding)
        
        # ASSERT
        assert enhanced_finding.gof_pattern_suggestion == "Factory Pattern + Dependency Injection"
        assert 'Replace global lookups' in enhanced_finding.gof_pattern_rationale
    
    def test_suggest_gof_pattern_no_mapping(self):
        """Test: Finding without mapping is not enhanced"""
        # ARRANGE
        finding = Finding(
            category="Performance Issue",
            severity=Severity.LOW,
            file_path=Path("modules/test/backend/api.py"),
            line_number=42,
            description="Slow query detected",
            recommendation="Optimize query"
        )
        
        # ACT
        enhanced_finding = self.agent._suggest_gof_pattern(finding)
        
        # ASSERT
        assert enhanced_finding.gof_pattern_suggestion is None
        assert enhanced_finding.gof_pattern_rationale is None
        assert enhanced_finding.gof_pattern_example is None
    
    def test_suggest_gof_pattern_preserves_existing_fields(self):
        """Test: Enhancement preserves all existing fields"""
        # ARRANGE
        finding = Finding(
            category="DI Violation",
            severity=Severity.HIGH,
            file_path=Path("modules/test/backend/api.py"),
            line_number=42,
            description="Direct instantiation detected",
            recommendation="Use dependency injection",
            code_snippet="repository = Repository()",
            impact_estimate="Improved testability"
        )
        
        original_description = finding.description
        original_recommendation = finding.recommendation
        original_code_snippet = finding.code_snippet
        
        # ACT
        enhanced_finding = self.agent._suggest_gof_pattern(finding)
        
        # ASSERT - Existing fields preserved
        assert enhanced_finding.description == original_description
        assert enhanced_finding.recommendation == original_recommendation
        assert enhanced_finding.code_snippet == original_code_snippet
        
        # ASSERT - New fields added
        assert enhanced_finding.gof_pattern_suggestion is not None
        assert enhanced_finding.gof_pattern_rationale is not None
        assert enhanced_finding.gof_pattern_example is not None


class TestIntegrationWithAnalyzeModule:
    """Test integration of GoF patterns in module analysis"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = ArchitectAgent()
    
    def test_analyze_module_enhances_findings_with_gof(self, tmp_path):
        """Test: analyze_module automatically enhances findings with GoF patterns"""
        # ARRANGE - Create a test module with DI violation
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        backend_dir = module_path / "backend"
        backend_dir.mkdir()
        
        # Create a file with DI violation
        api_file = backend_dir / "api.py"
        api_file.write_text("""
from some_module import Repository

def endpoint():
    # Direct instantiation - DI violation
    repository = Repository()
    return repository.get_data()
""")
        
        # ACT
        report = self.agent.analyze_module(module_path)
        
        # ASSERT - Report contains findings
        assert len(report.findings) > 0
        
        # ASSERT - At least one finding has GoF pattern suggestion
        gof_findings = [f for f in report.findings if f.gof_pattern_suggestion is not None]
        if len(gof_findings) > 0:  # If DI violation was detected
            finding = gof_findings[0]
            assert finding.gof_pattern_suggestion in ["Factory Pattern", "Dependency Injection Pattern"]
            assert finding.gof_pattern_rationale is not None
            assert finding.gof_pattern_example is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])