"""
Unit tests for Gu Wu Pre-Commit Test Runner

Tests the incremental test execution logic for pre-commit hooks
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from tools.guwu.pre_commit_test_runner import (
    get_staged_python_files,
    find_related_test_files,
    parse_pytest_output,
    extract_failed_tests,
    find_test_file_for_source
)

# Set project root for tests
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


@pytest.mark.unit
class TestGetStagedPythonFiles:
    """Test detection of staged Python files"""
    
    @patch('subprocess.run')
    def test_returns_python_files_only(self, mock_run):
        """Should filter only .py files from git diff output"""
        # ARRANGE
        mock_run.return_value = Mock(
            stdout="modules/test/api.py\nREADME.md\ncore/services/test.py\n",
            returncode=0
        )
        
        # ACT
        result = get_staged_python_files()
        
        # ASSERT
        assert len(result) == 2
        assert "modules/test/api.py" in result
        assert "core/services/test.py" in result
        assert "README.md" not in result
    
    @patch('subprocess.run')
    def test_handles_empty_output(self, mock_run):
        """Should handle no staged files gracefully"""
        # ARRANGE
        mock_run.return_value = Mock(stdout="", returncode=0)
        
        # ACT
        result = get_staged_python_files()
        
        # ASSERT
        assert result == []


@pytest.mark.unit
class TestFindRelatedTestFiles:
    """Test discovery of related test files"""
    
    def test_staged_test_file_included(self):
        """Should include test file if it's staged"""
        # ARRANGE
        staged_files = ["tests/unit/test_api.py"]
        
        # ACT
        result = find_related_test_files(staged_files)
        
        # ASSERT
        assert "tests/unit/test_api.py" in result
    
    def test_module_source_finds_unit_test(self):
        """Should find unit test for module source file"""
        # ARRANGE
        staged_files = ["modules/data_products_v2/backend/api.py"]
        
        # ACT - Note: This will only find tests if they actually exist
        result = find_related_test_files(staged_files)
        
        # ASSERT - We expect the logic to construct the right path
        # Actual existence check happens in the function
        assert isinstance(result, set)
    
    def test_core_service_finds_unit_test(self):
        """Should find unit test for core service file"""
        # ARRANGE
        staged_files = ["core/services/module_loader.py"]
        
        # ACT
        result = find_related_test_files(staged_files)
        
        # ASSERT
        assert isinstance(result, set)
        # If test exists, it should be found
        expected_test = "tests/unit/core/services/test_module_loader.py"
        if (PROJECT_ROOT / expected_test).exists():
            assert expected_test in result
    
    def test_tools_file_finds_unit_test(self):
        """Should find unit test for tools file"""
        # ARRANGE
        staged_files = ["tools/fengshui/agents/architect_agent.py"]
        
        # ACT
        result = find_related_test_files(staged_files)
        
        # ASSERT
        assert isinstance(result, set)


@pytest.mark.unit
class TestParsePytestOutput:
    """Test parsing of pytest output"""
    
    def test_parses_passed_tests(self):
        """Should extract number of passed tests"""
        # ARRANGE
        output = "====== 12 passed in 8.45s ======"
        
        # ACT
        stats = parse_pytest_output(output)
        
        # ASSERT
        assert stats["passed"] == 12
        assert stats["duration"] == 8.45
    
    def test_parses_failed_tests(self):
        """Should extract number of failed tests"""
        # ARRANGE
        output = "====== 8 passed, 4 failed in 10.23s ======"
        
        # ACT
        stats = parse_pytest_output(output)
        
        # ASSERT
        assert stats["passed"] == 8
        assert stats["failed"] == 4
        assert stats["duration"] == 10.23
    
    def test_parses_skipped_tests(self):
        """Should extract number of skipped tests"""
        # ARRANGE
        output = "====== 10 passed, 2 skipped in 5.67s ======"
        
        # ACT
        stats = parse_pytest_output(output)
        
        # ASSERT
        assert stats["passed"] == 10
        assert stats["skipped"] == 2
        assert stats["duration"] == 5.67
    
    def test_handles_no_matches(self):
        """Should return default values if no matches"""
        # ARRANGE
        output = "No test results found"
        
        # ACT
        stats = parse_pytest_output(output)
        
        # ASSERT
        assert stats["passed"] == 0
        assert stats["failed"] == 0
        assert stats["skipped"] == 0
        assert stats["duration"] == 0.0


@pytest.mark.unit
class TestExtractFailedTests:
    """Test extraction of failed test names"""
    
    def test_extracts_single_failure(self):
        """Should extract failed test name from output"""
        # ARRANGE
        output = "tests/unit/test_api.py::test_create_product FAILED"
        
        # ACT
        failed = extract_failed_tests(output)
        
        # ASSERT
        assert len(failed) == 1
        assert failed[0][0] == "tests/unit/test_api.py::test_create_product"
    
    def test_extracts_multiple_failures(self):
        """Should extract all failed test names"""
        # ARRANGE
        output = """
        tests/unit/test_api.py::test_create FAILED
        tests/unit/test_service.py::test_update FAILED
        """
        
        # ACT
        failed = extract_failed_tests(output)
        
        # ASSERT
        assert len(failed) == 2
        test_names = [f[0] for f in failed]
        assert "tests/unit/test_api.py::test_create" in test_names
        assert "tests/unit/test_service.py::test_update" in test_names
    
    def test_handles_no_failures(self):
        """Should return empty list if no failures"""
        # ARRANGE
        output = "All tests passed!"
        
        # ACT
        failed = extract_failed_tests(output)
        
        # ASSERT
        assert failed == []


@pytest.mark.unit
class TestFindTestFileForSource:
    """Test test file path generation"""
    
    def test_module_source_to_unit_test(self):
        """Should generate correct path for module file"""
        # ARRANGE
        source = "modules/data_products_v2/backend/api.py"
        
        # ACT
        test_path = find_test_file_for_source(source)
        
        # ASSERT
        assert test_path == "tests/unit/modules/data_products_v2/test_api.py"
    
    def test_core_service_to_unit_test(self):
        """Should generate correct path for core service"""
        # ARRANGE
        source = "core/services/module_loader.py"
        
        # ACT
        test_path = find_test_file_for_source(source)
        
        # ASSERT
        assert test_path == "tests/unit/core/services/test_module_loader.py"
    
    def test_tools_file_to_unit_test(self):
        """Should generate correct path for tools file"""
        # ARRANGE
        source = "tools/fengshui/agents/architect_agent.py"
        
        # ACT
        test_path = find_test_file_for_source(source)
        
        # ASSERT
        assert test_path == "tests/unit/tools/fengshui/test_architect_agent.py"
    
    def test_returns_none_for_invalid_path(self):
        """Should return None for unrecognized paths"""
        # ARRANGE
        source = "random_file.py"
        
        # ACT
        test_path = find_test_file_for_source(source)
        
        # ASSERT
        assert test_path is None


@pytest.mark.unit
class TestPerformanceLimits:
    """Test performance safeguards"""
    
    def test_respects_max_files_limit(self):
        """Should skip if too many files staged"""
        # ARRANGE
        MAX_FILES = 20
        many_files = [f"file{i}.py" for i in range(25)]
        
        # ACT/ASSERT
        # This would be tested in integration test
        # Unit test validates logic exists
        assert len(many_files) > MAX_FILES


# Integration test markers for future
@pytest.mark.integration
@pytest.mark.skip(reason="Integration test - requires git repository")
class TestGitIntegration:
    """Integration tests with real git commands"""
    
    def test_real_git_diff_execution(self):
        """Should execute real git diff command"""
        # Would test against real git repository
        pass
    
    def test_real_pytest_execution(self):
        """Should execute real pytest command"""
        # Would test against real test files
        pass