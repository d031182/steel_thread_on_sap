"""
Unit tests for Documentation Agent

Tests documentation quality analysis:
- README completeness checking
- Docstring coverage validation
- Documentation structure compliance
"""

import pytest
from pathlib import Path
from tools.fengshui.agents import DocumentationAgent, Severity


class TestDocumentationAgentInitialization:
    """Test agent initialization and capabilities"""
    
    def test_agent_initializes_correctly(self):
        # ARRANGE & ACT
        agent = DocumentationAgent()
        
        # ASSERT
        assert agent.name == "documentation"
        assert agent.logger is not None
        assert agent.min_readme_length == 100
        assert agent.min_docstring_length == 20
    
    def test_get_capabilities_returns_doc_checks(self):
        # ARRANGE
        agent = DocumentationAgent()
        
        # ACT
        capabilities = agent.get_capabilities()
        
        # ASSERT
        assert len(capabilities) == 6
        assert "README" in capabilities[0]
        assert "Docstring" in capabilities[1]
        assert "documentation" in capabilities[3].lower()


class TestREADMEChecking:
    """Test README.md validation"""
    
    def test_detects_missing_readme(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        # No README.md created
        
        # ACT
        findings = agent._check_readme(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Missing README"
        assert findings[0].severity == Severity.MEDIUM
        assert "Create README" in findings[0].recommendation
    
    def test_detects_insufficient_readme(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        readme = tmp_path / 'README.md'
        readme.write_text("# Module\nShort description")  # < 100 chars
        
        # ACT
        findings = agent._check_readme(tmp_path)
        
        # ASSERT
        assert len(findings) >= 1  # May also flag missing sections
        insufficient_findings = [f for f in findings if f.category == "Insufficient README"]
        assert len(insufficient_findings) == 1
        assert insufficient_findings[0].severity == Severity.LOW
    
    def test_detects_missing_overview_section(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        readme = tmp_path / 'README.md'
        readme.write_text("""
# Module Name

## Usage
How to use this module.

## API Reference
List of APIs.
""")  # Missing overview/introduction
        
        # ACT
        findings = agent._check_readme(tmp_path)
        
        # ASSERT
        overview_findings = [f for f in findings if 'overview' in f.description.lower()]
        assert len(overview_findings) == 1
    
    def test_allows_comprehensive_readme(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        readme = tmp_path / 'README.md'
        readme.write_text("""
# Module Name

## Overview
This module provides comprehensive functionality for data processing.

## Usage
Here's how to use this module:
```python
from module import Service
service = Service()
```

## API Reference
- `get_data()`: Retrieves data
- `process()`: Processes data
""")
        
        # ACT
        findings = agent._check_readme(tmp_path)
        
        # ASSERT
        assert len(findings) == 0  # Comprehensive README


class TestDocstringChecking:
    """Test docstring validation"""
    
    def test_detects_missing_function_docstring(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text("""
def public_function(param):
    return param * 2
""")
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Missing Docstring"
        assert findings[0].severity == Severity.LOW
        assert "public_function" in findings[0].description
    
    def test_detects_missing_class_docstring(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'models.py'
        py_file.write_text("""
class DataProcessor:
    def process(self):
        pass
""")
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) >= 1
        class_findings = [f for f in findings if 'DataProcessor' in f.description]
        assert len(class_findings) == 1
    
    def test_detects_insufficient_docstring(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text('''
def calculate(x, y):
    """Add"""
    return x + y
''')  # Docstring < 20 chars
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Insufficient Docstring"
        assert "too brief" in findings[0].description
    
    def test_detects_placeholder_docstring(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text('''
def process_data(items):
    """TODO: Add documentation"""
    return items
''')
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Placeholder Docstring"
        assert "placeholder" in findings[0].description.lower()
    
    def test_allows_private_methods_without_docstrings(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text("""
def _private_helper():
    return True
""")
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) == 0  # Private methods don't need docstrings
    
    def test_allows_well_documented_functions(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'service.py'
        py_file.write_text('''
def calculate_total(items):
    """
    Calculate total value of items
    
    Args:
        items: List of items to process
        
    Returns:
        Total value as float
    """
    return sum(item.value for item in items)
''')
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) == 0  # Well documented


class TestModuleAnalysis:
    """Test full module analysis"""
    
    def test_analyzes_complete_module(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        backend_dir = tmp_path / 'backend'
        backend_dir.mkdir()
        
        # Create service without docstrings
        (backend_dir / 'service.py').write_text("""
def public_method():
    return True
""")
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.agent_name == "documentation"
        assert report.module_path == tmp_path
        assert len(report.findings) >= 2  # Missing README + missing docstring
        assert report.metrics['files_checked'] >= 1
    
    def test_handles_invalid_module_path(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        invalid_path = tmp_path / "nonexistent"
        
        # ACT
        report = agent.analyze_module(invalid_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "invalid" in report.summary.lower()
    
    def test_generates_clean_report_when_well_documented(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        
        # Create comprehensive README
        (tmp_path / 'README.md').write_text("""
# Module Name

## Overview
This module provides data processing capabilities.

## Usage
Use it like this.

## API Reference
Methods available.
""")
        
        # Create well-documented Python file
        (tmp_path / 'service.py').write_text('''
def process():
    """Process data with comprehensive algorithm"""
    return True
''')
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "no issues" in report.summary.lower()
    
    def test_skips_test_files(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        test_file = tmp_path / 'test_something.py'
        test_file.write_text("""
def test_feature():
    pass  # Test without docstring - should be ignored
""")
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        # Should only report missing README, not test file docstrings
        assert len([f for f in report.findings if 'test_feature' in str(f.description)]) == 0


class TestMetrics:
    """Test metrics calculation"""
    
    def test_metrics_count_findings_by_severity(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        
        # Create file with multiple doc issues
        (tmp_path / 'service.py').write_text('''
def func1():
    pass  # Missing docstring (LOW)

def func2():
    """TODO"""  # Placeholder (LOW)
    pass

def func3():
    """Short"""  # Insufficient (LOW)
    pass
''')
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.metrics['medium_count'] >= 1  # Missing README
        assert report.metrics['low_count'] >= 3  # Docstring issues
    
    def test_metrics_count_files_checked(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        (tmp_path / 'file1.py').write_text('def f(): """Doc"""; pass')
        (tmp_path / 'file2.py').write_text('def g(): """Doc"""; pass')
        (tmp_path / 'README.md').write_text('x' * 200)  # Valid README
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.metrics['files_checked'] == 2  # 2 Python files


class TestErrorHandling:
    """Test error handling"""
    
    def test_handles_invalid_python_gracefully(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'invalid.py'
        py_file.write_text('this is not valid python {{{')
        
        # ACT (should not crash)
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert isinstance(findings, list)
    
    def test_handles_unreadable_readme_gracefully(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        readme = tmp_path / 'README.md'
        readme.touch()
        readme.chmod(0o000)  # Make unreadable (Unix-like systems)
        
        # ACT (should not crash)
        try:
            findings = agent._check_readme(tmp_path)
            assert isinstance(findings, list)
        except PermissionError:
            # Windows may not support chmod 000, skip test
            pytest.skip("Cannot test unreadable file on this platform")
        finally:
            # Restore permissions
            try:
                readme.chmod(0o644)
            except:
                pass


class TestRecommendations:
    """Test recommendation quality"""
    
    def test_missing_readme_recommendation_is_actionable(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        
        # ACT
        findings = agent._check_readme(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert "purpose" in findings[0].recommendation.lower()
        assert "usage" in findings[0].recommendation.lower()
    
    def test_missing_docstring_recommendation_includes_components(self, tmp_path):
        # ARRANGE
        agent = DocumentationAgent()
        py_file = tmp_path / 'api.py'
        py_file.write_text("""
def get_data(param1, param2):
    return param1 + param2
""")
        
        # ACT
        findings = agent._check_docstrings(py_file)
        
        # ASSERT
        assert len(findings) == 1
        rec = findings[0].recommendation.lower()
        assert "parameters" in rec or "args" in rec
        assert "return" in rec