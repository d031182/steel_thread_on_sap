"""
Unit tests for Repository Pattern Detector in Feng Shui ArchitectAgent
"""

import pytest
from pathlib import Path
from tools.fengshui.agents.architect_agent import ArchitectAgent
from tools.fengshui.agents.base_agent import Severity


class TestRepositoryPatternDetector:
    """Test Repository Pattern violation detection"""
    
    def test_detector_registered(self):
        """Test that repository_pattern detector is registered"""
        agent = ArchitectAgent()
        assert 'repository_pattern' in agent.pattern_detectors
    
    def test_detect_private_implementation_import(self, tmp_path):
        """Test detection of private implementation imports (CRITICAL)"""
        # Create test file with violation
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            "from core.repositories._sqlite_repository import _SqliteRepository\n"
            "repo = _SqliteRepository(db_path='test.db')\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find CRITICAL violation
        assert len(findings) > 0
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) > 0
        assert "_sqlite_repository" in critical_findings[0].code_snippet
    
    def test_detect_private_attribute_access(self, tmp_path):
        """Test detection of private attribute access (HIGH)"""
        # Create test file with violation
        test_file = tmp_path / "test_service.py"
        test_file.write_text(
            "def get_conn(repo):\n"
            "    return repo._connection  # Violation\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find HIGH violation
        assert len(findings) > 0
        high_findings = [f for f in findings if f.severity == Severity.HIGH]
        assert len(high_findings) > 0
        assert "_connection" in high_findings[0].description
    
    def test_detect_deprecated_datasource(self, tmp_path):
        """Test detection of deprecated DataSource pattern (MEDIUM)"""
        # Create test file with violation
        test_file = tmp_path / "test_api.py"
        test_file.write_text(
            "from flask import current_app\n"
            "data_source = current_app.sqlite_data_source\n"
            "conn = data_source.get_connection()\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find MEDIUM violations
        assert len(findings) > 0
        medium_findings = [f for f in findings if f.severity == Severity.MEDIUM]
        assert len(medium_findings) >= 2  # sqlite_data_source + get_connection
        assert any("sqlite_data_source" in f.code_snippet for f in medium_findings)
    
    def test_detect_direct_database_import(self, tmp_path):
        """Test detection of direct database library imports (MEDIUM)"""
        # Create test file with violation
        test_file = tmp_path / "test_query.py"
        test_file.write_text(
            "import sqlite3\n"
            "conn = sqlite3.connect('database.db')\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find MEDIUM violation
        assert len(findings) > 0
        medium_findings = [f for f in findings if f.severity == Severity.MEDIUM]
        assert len(medium_findings) > 0
        assert any("sqlite3" in f.code_snippet for f in medium_findings)
    
    def test_skip_core_directory(self, tmp_path):
        """Test that core/ directory is skipped (allowed to use implementations)"""
        # Create core directory structure
        core_dir = tmp_path / "core" / "repositories"
        core_dir.mkdir(parents=True)
        
        test_file = core_dir / "_sqlite_repository.py"
        test_file.write_text(
            "import sqlite3\n"
            "class _SqliteRepository:\n"
            "    def __init__(self):\n"
            "        self._connection = sqlite3.connect('db')\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find NO violations (core/ is allowed)
        assert len(findings) == 0
    
    def test_skip_test_files(self, tmp_path):
        """Test that test files are skipped"""
        # Create tests directory
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_repository.py"
        test_file.write_text(
            "from core.repositories._sqlite_repository import _SqliteRepository\n"
            "def test_repository():\n"
            "    repo = _SqliteRepository(db_path='test.db')\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find NO violations (tests/ is skipped)
        assert len(findings) == 0
    
    def test_correct_usage_no_violations(self, tmp_path):
        """Test that correct Repository Pattern usage has no violations"""
        # Create test file with CORRECT usage
        test_file = tmp_path / "correct_service.py"
        test_file.write_text(
            "from flask import current_app\n"
            "from core.repositories import AbstractRepository\n"
            "\n"
            "def get_products():\n"
            "    repository = current_app.sqlite_repository\n"
            "    return repository.get_data_products()\n"
        )
        
        agent = ArchitectAgent()
        findings = agent._detect_repository_violations(tmp_path)
        
        # Should find NO violations
        assert len(findings) == 0
    
    def test_real_module_p2p_dashboard(self):
        """Integration test: Analyze real p2p_dashboard module"""
        module_path = Path('modules/p2p_dashboard')
        
        if not module_path.exists():
            pytest.skip("p2p_dashboard module not found")
        
        agent = ArchitectAgent()
        report = agent.analyze_module(module_path)
        
        # Should complete analysis
        assert report.metrics['files_analyzed'] > 0
        
        # May have deprecated DataSource usage (backward compatibility)
        # but should have NO CRITICAL violations
        assert report.metrics['critical_count'] == 0