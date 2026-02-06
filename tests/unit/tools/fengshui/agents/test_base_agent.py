"""
Unit tests for BaseAgent interface

Tests the abstract base class and data structures for Feng Shui agents.
"""

import pytest
from pathlib import Path
from tools.fengshui.agents.base_agent import (
    BaseAgent,
    Finding,
    Severity,
    AgentReport
)


# Mock concrete agent for testing
class MockAgent(BaseAgent):
    """Mock agent implementation for testing"""
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """Mock implementation"""
        if not self.validate_module_path(module_path):
            return self._create_empty_report(module_path)
        
        # Create mock findings
        findings = [
            Finding(
                category="Test Category",
                severity=Severity.HIGH,
                file_path=module_path / "test.py",
                line_number=10,
                description="Test finding",
                recommendation="Test recommendation"
            )
        ]
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=0.5,
            findings=findings,
            metrics={'test_metric': 1.0},
            summary="Mock analysis complete"
        )
    
    def get_capabilities(self):
        """Mock capabilities"""
        return ["Test capability 1", "Test capability 2"]


class TestSeverity:
    """Test Severity enum"""
    
    def test_severity_levels(self):
        """Test all severity levels exist"""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestFinding:
    """Test Finding data class"""
    
    def test_finding_creation(self):
        """Test creating a Finding"""
        finding = Finding(
            category="DI Violation",
            severity=Severity.CRITICAL,
            file_path=Path("test/file.py"),
            line_number=42,
            description="Test description",
            recommendation="Test recommendation",
            code_snippet="test_code()"
        )
        
        assert finding.category == "DI Violation"
        assert finding.severity == Severity.CRITICAL
        assert finding.file_path == Path("test/file.py")
        assert finding.line_number == 42
        assert finding.description == "Test description"
        assert finding.recommendation == "Test recommendation"
        assert finding.code_snippet == "test_code()"
    
    def test_finding_to_dict(self):
        """Test Finding serialization"""
        finding = Finding(
            category="Test Category",
            severity=Severity.HIGH,
            file_path=Path("test.py"),
            line_number=10,
            description="Test",
            recommendation="Fix it"
        )
        
        result = finding.to_dict()
        
        assert result['category'] == "Test Category"
        assert result['severity'] == "high"
        assert result['file_path'] == "test.py"
        assert result['line_number'] == 10
        assert result['description'] == "Test"
        assert result['recommendation'] == "Fix it"
        assert result['code_snippet'] is None


class TestAgentReport:
    """Test AgentReport data class"""
    
    def test_report_creation(self):
        """Test creating an AgentReport"""
        findings = [
            Finding(
                category="Test",
                severity=Severity.CRITICAL,
                file_path=Path("test.py"),
                line_number=1,
                description="Critical issue",
                recommendation="Fix now"
            ),
            Finding(
                category="Test",
                severity=Severity.HIGH,
                file_path=Path("test.py"),
                line_number=2,
                description="High issue",
                recommendation="Fix soon"
            )
        ]
        
        report = AgentReport(
            agent_name="test_agent",
            module_path=Path("modules/test"),
            execution_time_seconds=1.5,
            findings=findings,
            metrics={'violations': 2},
            summary="Test complete"
        )
        
        assert report.agent_name == "test_agent"
        assert report.module_path == Path("modules/test")
        assert report.execution_time_seconds == 1.5
        assert len(report.findings) == 2
        assert report.metrics['violations'] == 2
        assert report.summary == "Test complete"
    
    def test_report_severity_counts(self):
        """Test severity counting methods"""
        findings = [
            Finding("Test", Severity.CRITICAL, Path("a.py"), 1, "Test", "Fix"),
            Finding("Test", Severity.CRITICAL, Path("b.py"), 2, "Test", "Fix"),
            Finding("Test", Severity.HIGH, Path("c.py"), 3, "Test", "Fix"),
            Finding("Test", Severity.MEDIUM, Path("d.py"), 4, "Test", "Fix"),
            Finding("Test", Severity.LOW, Path("e.py"), 5, "Test", "Fix"),
        ]
        
        report = AgentReport(
            agent_name="test",
            module_path=Path("test"),
            execution_time_seconds=1.0,
            findings=findings
        )
        
        assert report.get_critical_count() == 2
        assert report.get_high_count() == 1
        assert report.get_medium_count() == 1
        assert report.get_low_count() == 1
    
    def test_report_to_dict(self):
        """Test AgentReport serialization"""
        finding = Finding(
            category="Test",
            severity=Severity.HIGH,
            file_path=Path("test.py"),
            line_number=10,
            description="Test",
            recommendation="Fix"
        )
        
        report = AgentReport(
            agent_name="test_agent",
            module_path=Path("modules/test"),
            execution_time_seconds=1.5,
            findings=[finding],
            metrics={'count': 1},
            summary="Done"
        )
        
        result = report.to_dict()
        
        assert result['agent_name'] == "test_agent"
        assert result['module_path'] == str(Path("modules/test"))  # Windows-compatible
        assert result['execution_time_seconds'] == 1.5
        assert len(result['findings']) == 1
        assert result['findings'][0]['category'] == "Test"
        assert result['metrics']['count'] == 1
        assert result['summary'] == "Done"


class TestBaseAgent:
    """Test BaseAgent abstract base class"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = MockAgent("test_agent")
        
        assert agent.name == "test_agent"
        assert agent.logger.name == "fengshui.agents.test_agent"
    
    def test_validate_module_path_valid(self, tmp_path):
        """Test path validation with valid directory"""
        agent = MockAgent("test")
        
        # tmp_path is a valid directory
        assert agent.validate_module_path(tmp_path) is True
    
    def test_validate_module_path_nonexistent(self):
        """Test path validation with non-existent path"""
        agent = MockAgent("test")
        invalid_path = Path("/nonexistent/path/12345")
        
        assert agent.validate_module_path(invalid_path) is False
    
    def test_validate_module_path_file(self, tmp_path):
        """Test path validation with file instead of directory"""
        agent = MockAgent("test")
        
        # Create a file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        assert agent.validate_module_path(test_file) is False
    
    def test_analyze_module_valid_path(self, tmp_path):
        """Test analyze_module with valid path"""
        agent = MockAgent("test")
        
        report = agent.analyze_module(tmp_path)
        
        assert report.agent_name == "test"
        assert report.module_path == tmp_path
        assert len(report.findings) == 1
        assert report.findings[0].severity == Severity.HIGH
    
    def test_analyze_module_invalid_path(self):
        """Test analyze_module with invalid path"""
        agent = MockAgent("test")
        invalid_path = Path("/nonexistent/12345")
        
        report = agent.analyze_module(invalid_path)
        
        assert report.agent_name == "test"
        assert report.execution_time_seconds == 0.0
        assert len(report.findings) == 0
        assert report.summary == "Invalid module path"
    
    def test_get_capabilities(self):
        """Test get_capabilities method"""
        agent = MockAgent("test")
        
        capabilities = agent.get_capabilities()
        
        assert len(capabilities) == 2
        assert "Test capability 1" in capabilities
        assert "Test capability 2" in capabilities
    
    def test_create_empty_report(self):
        """Test _create_empty_report helper"""
        agent = MockAgent("test")
        module_path = Path("modules/test")
        
        report = agent._create_empty_report(module_path, "Test reason")
        
        assert report.agent_name == "test"
        assert report.module_path == module_path
        assert report.execution_time_seconds == 0.0
        assert len(report.findings) == 0
        assert report.metrics == {}
        assert report.summary == "Test reason"


@pytest.mark.unit
@pytest.mark.fast
class TestBaseAgentIntegration:
    """Integration tests for BaseAgent"""
    
    def test_full_workflow(self, tmp_path):
        """Test complete agent workflow"""
        # ARRANGE
        agent = MockAgent("integration_test")
        
        # Create test module structure
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        (module_path / "test.py").write_text("# test file")
        
        # ACT
        report = agent.analyze_module(module_path)
        
        # ASSERT
        assert report.agent_name == "integration_test"
        assert report.module_path == module_path
        assert report.execution_time_seconds > 0
        assert len(report.findings) > 0
        
        # Test serialization
        report_dict = report.to_dict()
        assert 'agent_name' in report_dict
        assert 'findings' in report_dict