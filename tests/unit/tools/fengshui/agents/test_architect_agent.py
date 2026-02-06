"""
Unit tests for ArchitectAgent

Tests architecture analysis capabilities:
- DI violation detection
- SOLID principle checks
- Large class detection
- Report generation
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from tools.fengshui.agents.architect_agent import ArchitectAgent
from tools.fengshui.agents.base_agent import Severity, Finding, AgentReport


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentInitialization:
    """Test ArchitectAgent initialization"""
    
    def test_init_creates_agent_with_correct_name(self):
        """Test agent initializes with correct name"""
        # ARRANGE & ACT
        agent = ArchitectAgent()
        
        # ASSERT
        assert agent.name == "architect"
        assert hasattr(agent, 'pattern_detectors')
        assert len(agent.pattern_detectors) == 3
    
    def test_get_capabilities_returns_list(self):
        """Test get_capabilities returns capability list"""
        # ARRANGE
        agent = ArchitectAgent()
        
        # ACT
        capabilities = agent.get_capabilities()
        
        # ASSERT
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "Dependency Injection" in capabilities[0]


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentDIDetection:
    """Test DI violation detection"""
    
    def test_detect_connection_access_violation(self):
        """Test detects .connection attribute access"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "test_service.py"
            
            test_file.write_text(
                "class MyService:\n"
                "    def connect(self, data_source):\n"
                "        conn = data_source.connection  # DI violation\n"
                "        return conn\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "DI Violation"
            assert findings[0].severity == Severity.HIGH
            assert "connection" in findings[0].description
            assert findings[0].line_number == 3
    
    def test_detect_service_access_violation(self):
        """Test detects .service attribute access"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "test_api.py"
            
            test_file.write_text(
                "def get_data(provider):\n"
                "    svc = provider.service  # DI violation\n"
                "    return svc.query()\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "DI Violation"
            assert "service" in findings[0].description
            assert findings[0].line_number == 2
    
    def test_detect_db_path_access_violation(self):
        """Test detects .db_path attribute access"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "test_config.py"
            
            test_file.write_text(
                "def setup_database(resolver):\n"
                "    path = resolver.db_path  # DI violation\n"
                "    return path\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "DI Violation"
            assert "db_path" in findings[0].description
            assert findings[0].line_number == 2
    
    def test_detect_multiple_violations_in_single_file(self):
        """Test detects multiple DI violations in same file"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "test_multi.py"
            
            test_file.write_text(
                "def bad_function(ds):\n"
                "    conn = ds.connection\n"
                "    svc = ds.service\n"
                "    path = ds.db_path\n"
                "    return conn, svc, path\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 3
            assert all(f.category == "DI Violation" for f in findings)
            assert all(f.severity == Severity.HIGH for f in findings)
    
    def test_skips_files_in_tests_directory(self):
        """Test skips files in tests/ directories"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            tests_dir = module_path / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_something.py"
            
            test_file.write_text(
                "def test_function(ds):\n"
                "    conn = ds.connection  # Should be ignored (in tests/)\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 0


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentLargeClassDetection:
    """Test large class detection (SRP violations)"""
    
    def test_detect_large_class_over_500_loc(self):
        """Test detects classes over 500 LOC"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "large_class.py"
            
            # Create class with >500 lines
            lines = ["class GodObject:"] + ["    pass"] * 550
            test_file.write_text("\n".join(lines), encoding='utf-8')
            
            # ACT
            findings = agent._detect_large_classes(module_path)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "Large Class (SRP Violation)"
            assert findings[0].severity == Severity.MEDIUM
            assert "551 lines" in findings[0].description
            assert "GodObject" in findings[0].description
    
    def test_ignores_small_classes_under_500_loc(self):
        """Test ignores classes under 500 LOC"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "small_class.py"
            
            # Create class with <500 lines
            lines = ["class SmallClass:"] + ["    pass"] * 100
            test_file.write_text("\n".join(lines), encoding='utf-8')
            
            # ACT
            findings = agent._detect_large_classes(module_path)
            
            # ASSERT
            assert len(findings) == 0
    
    def test_skips_files_in_tests_directory_for_large_class(self):
        """Test skips files in tests/ directories for large class detection"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            tests_dir = module_path / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "test_large.py"
            
            lines = ["class TestLarge:"] + ["    pass"] * 600
            test_file.write_text("\n".join(lines), encoding='utf-8')
            
            # ACT
            findings = agent._detect_large_classes(module_path)
            
            # ASSERT
            assert len(findings) == 0


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentModuleAnalysis:
    """Test complete module analysis"""
    
    def test_analyze_module_with_no_violations(self):
        """Test analysis of clean module"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "clean_code.py"
            
            test_file.write_text(
                "class CleanService:\n"
                "    def __init__(self, connection):\n"
                "        self._connection = connection\n"
                "    \n"
                "    def query(self):\n"
                "        return self._connection.execute('SELECT 1')\n",
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.agent_name == "architect"
            assert report.module_path == module_path
            assert len(report.findings) == 0
            assert report.metrics['files_analyzed'] == 1
            assert "No violations" in report.summary
    
    def test_analyze_module_with_violations(self):
        """Test analysis of module with violations"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "bad_code.py"
            
            test_file.write_text(
                "class BadService:\n"
                "    def query(self, provider):\n"
                "        conn = provider.connection  # DI violation\n"
                "        return conn.execute('SELECT 1')\n",
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.agent_name == "architect"
            assert len(report.findings) == 1
            assert report.findings[0].severity == Severity.HIGH
            assert report.metrics['high_count'] == 1
            assert "1 violations" in report.summary or "1 violation" in report.summary
    
    def test_analyze_module_with_multiple_issues(self):
        """Test analysis finds all issue types"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # File with DI violation
            file1 = module_path / "di_issue.py"
            file1.write_text(
                "def func(ds):\n"
                "    return ds.connection\n",
                encoding='utf-8'
            )
            
            # File with large class
            file2 = module_path / "large.py"
            lines = ["class Large:"] + ["    pass"] * 550
            file2.write_text("\n".join(lines), encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert len(report.findings) == 2
            assert report.metrics['files_analyzed'] == 2
            assert report.metrics['high_count'] == 1  # DI violation
            assert report.metrics['medium_count'] == 1  # Large class
    
    def test_analyze_invalid_module_path(self):
        """Test analysis with non-existent module path"""
        # ARRANGE
        agent = ArchitectAgent()
        invalid_path = Path("/nonexistent/path/to/module")
        
        # ACT
        report = agent.analyze_module(invalid_path)
        
        # ASSERT
        assert report.agent_name == "architect"
        assert len(report.findings) == 0
        assert report.execution_time_seconds == 0
        assert "Invalid module path" in report.summary
    
    def test_analyze_module_handles_syntax_errors_gracefully(self):
        """Test analysis continues despite syntax errors"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # Invalid syntax file
            bad_file = module_path / "syntax_error.py"
            bad_file.write_text(
                "def broken function(:\n"
                "    pass\n",
                encoding='utf-8'
            )
            
            # Valid file
            good_file = module_path / "good.py"
            good_file.write_text(
                "def func(ds):\n"
                "    return ds.connection\n",
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT - Should process good file despite bad file
            assert len(report.findings) >= 1  # At least the good file's violation
            assert report.metrics['files_analyzed'] == 2


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentReportGeneration:
    """Test report generation and metrics"""
    
    def test_report_contains_all_required_fields(self):
        """Test report has all required fields"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            (module_path / "test.py").write_text("pass", encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert hasattr(report, 'agent_name')
            assert hasattr(report, 'module_path')
            assert hasattr(report, 'execution_time_seconds')
            assert hasattr(report, 'findings')
            assert hasattr(report, 'metrics')
            assert hasattr(report, 'summary')
    
    def test_metrics_calculation_accuracy(self):
        """Test metrics are calculated correctly"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # 2 HIGH severity issues
            file1 = module_path / "file1.py"
            file1.write_text(
                "def f1(ds): return ds.connection\n"
                "def f2(ds): return ds.service\n",
                encoding='utf-8'
            )
            
            # 1 MEDIUM severity issue
            file2 = module_path / "file2.py"
            lines = ["class Big:"] + ["    pass"] * 550
            file2.write_text("\n".join(lines), encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.metrics['total_violations'] == 3
            assert report.metrics['high_count'] == 2
            assert report.metrics['medium_count'] == 1
            assert report.metrics['critical_count'] == 0
            assert report.metrics['files_analyzed'] == 2
    
    def test_summary_reflects_findings(self):
        """Test summary message reflects actual findings"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # Clean module
            (module_path / "clean.py").write_text("pass", encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert "No violations" in report.summary
            assert "✅" in report.summary
    
    def test_summary_shows_violation_counts(self):
        """Test summary includes violation counts"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "violations.py"
            
            test_file.write_text(
                "def f(ds): return ds.connection\n",
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert "1 violation" in report.summary.lower() or "1 violations" in report.summary
            assert "HIGH" in report.summary
            assert "⚠️" in report.summary


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentErrorHandling:
    """Test error handling and edge cases"""
    
    def test_handles_empty_module_directory(self):
        """Test handles module with no Python files"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.agent_name == "architect"
            assert len(report.findings) == 0
            assert report.metrics['files_analyzed'] == 0
    
    def test_handles_non_python_files(self):
        """Test ignores non-Python files"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # Create non-Python files
            (module_path / "readme.txt").write_text("README", encoding='utf-8')
            (module_path / "config.json").write_text("{}", encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.metrics['files_analyzed'] == 0
    
    def test_handles_nested_directory_structure(self):
        """Test analyzes nested directories correctly"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # Nested structure
            backend_dir = module_path / "backend"
            backend_dir.mkdir()
            
            (backend_dir / "api.py").write_text(
                "def f(ds): return ds.connection\n",
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert len(report.findings) == 1
            assert report.metrics['files_analyzed'] == 1
    
    def test_execution_time_is_recorded(self):
        """Test execution time is measured"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            (module_path / "test.py").write_text("pass", encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.execution_time_seconds > 0
            assert report.execution_time_seconds < 10  # Should be fast


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentCodeSnippets:
    """Test code snippet extraction"""
    
    def test_finding_includes_code_snippet(self):
        """Test findings include actual code snippet"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "snippet.py"
            
            test_file.write_text(
                "def bad_function(provider):\n"
                "    connection = provider.connection  # This is the snippet\n"
                "    return connection\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].code_snippet is not None
            assert "provider.connection" in findings[0].code_snippet


@pytest.mark.unit
@pytest.mark.fast
class TestArchitectAgentRecommendations:
    """Test recommendation quality"""
    
    def test_recommendations_are_actionable(self):
        """Test recommendations provide clear guidance"""
        # ARRANGE
        agent = ArchitectAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "test.py"
            
            test_file.write_text(
                "def f(ds): return ds.connection\n",
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._detect_di_violations(module_path)
            
            # ASSERT
            assert len(findings) == 1
            recommendation = findings[0].recommendation
            assert "constructor injection" in recommendation or "parameter passing" in recommendation
            assert "connection" in recommendation