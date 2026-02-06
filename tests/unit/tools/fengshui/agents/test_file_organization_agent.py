"""
Unit tests for File Organization Agent

Tests file placement and project structure validation:
- Root directory cleanliness
- scripts/ hierarchy (python/, test/, tmp/, sql/)
- docs/ hierarchy (knowledge vault structure)
- Obsolete file detection
- Module structure compliance
"""

import pytest
import os
from pathlib import Path
from datetime import datetime, timedelta
from tools.fengshui.agents import FileOrganizationAgent, Severity


class TestFileOrganizationAgentInitialization:
    """Test agent initialization and capabilities"""
    
    def test_agent_initializes_correctly(self):
        # ARRANGE & ACT
        agent = FileOrganizationAgent()
        
        # ASSERT
        assert agent.name == "file_organization"
        assert agent.logger is not None
        assert len(agent.allowed_root_files) > 0
    
    def test_get_capabilities_returns_organization_checks(self):
        # ARRANGE
        agent = FileOrganizationAgent()
        
        # ACT
        capabilities = agent.get_capabilities()
        
        # ASSERT
        assert len(capabilities) == 8
        assert "Root directory" in capabilities[0]
        assert "Misplaced file" in capabilities[1]
        assert "Obsolete" in capabilities[2]


class TestRootDirectoryValidation:
    """Test root directory cleanliness checks"""
    
    def test_allows_authorized_root_files(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'README.md').write_text('# Project\n')
        (tmp_path / 'package.json').write_text('{}\n')
        (tmp_path / '.gitignore').write_text('*.log\n')
        
        # ACT
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 0
    
    def test_detects_unauthorized_markdown_in_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'planning.md').write_text('# Planning\n')
        
        # ACT
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Root Directory Clutter"
        assert findings[0].severity == Severity.HIGH
        assert "docs/knowledge/" in findings[0].recommendation
    
    def test_detects_database_file_in_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'test.db').write_text('')
        
        # ACT
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].severity == Severity.HIGH
        assert "app/database/" in findings[0].recommendation
    
    def test_detects_log_file_in_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'debug.log').write_text('log data\n')
        
        # ACT
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].severity == Severity.MEDIUM
        assert "logs/" in findings[0].recommendation
    
    def test_detects_test_file_in_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'test_something.py').write_text('def test(): pass\n')
        
        # ACT
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert "tests/" in findings[0].recommendation


class TestScriptsDirectoryValidation:
    """Test scripts/ hierarchy validation"""
    
    def test_detects_test_script_in_python_dir(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        scripts_python = tmp_path / 'scripts' / 'python'
        scripts_python.mkdir(parents=True)
        (scripts_python / 'test_migration.py').write_text('def test(): pass\n')
        
        # ACT
        findings = agent._check_scripts_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Misplaced Script"
        assert findings[0].severity == Severity.MEDIUM
        assert "scripts/test/" in findings[0].recommendation
    
    def test_detects_check_script_in_python_dir(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        scripts_python = tmp_path / 'scripts' / 'python'
        scripts_python.mkdir(parents=True)
        (scripts_python / 'check_data.py').write_text('# check script\n')
        
        # ACT
        findings = agent._check_scripts_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert "check_" in findings[0].description
    
    def test_detects_old_tmp_files(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        scripts_tmp = tmp_path / 'scripts' / 'tmp'
        scripts_tmp.mkdir(parents=True)
        old_file = scripts_tmp / 'old_script.py'
        old_file.write_text('# old script\n')
        
        # Set modification time to 10 days ago
        ten_days_ago = (datetime.now() - timedelta(days=10)).timestamp()
        os.utime(old_file, (ten_days_ago, ten_days_ago))
        
        # ACT
        findings = agent._check_scripts_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Obsolete Temporary File"
        assert findings[0].severity == Severity.LOW
        assert "DELETE" in findings[0].recommendation


class TestDocsDirectoryValidation:
    """Test docs/ hierarchy validation"""
    
    def test_detects_markdown_in_docs_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        docs_dir = tmp_path / 'docs'
        docs_dir.mkdir()
        (docs_dir / 'random_doc.md').write_text('# Random\n')
        
        # ACT
        findings = agent._check_docs_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Documentation Misplacement"
        assert findings[0].severity == Severity.MEDIUM
        assert "docs/knowledge/" in findings[0].recommendation
    
    def test_allows_specific_audit_docs_in_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        docs_dir = tmp_path / 'docs'
        docs_dir.mkdir()
        (docs_dir / 'FENG_SHUI_AUDIT_2026-02-01.md').write_text('# Audit\n')
        (docs_dir / 'FENG_SHUI_ROUTINE_REQUIREMENTS.md').write_text('# Requirements\n')
        
        # ACT
        findings = agent._check_docs_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 0  # These specific files are allowed
    
    def test_detects_stale_planning_docs(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        planning_dir = tmp_path / 'docs' / 'planning'
        planning_dir.mkdir(parents=True)
        stale_doc = planning_dir / 'old_plan.md'
        stale_doc.write_text('# Old plan\n')
        
        # Set modification time to 35 days ago
        thirty_five_days_ago = (datetime.now() - timedelta(days=35)).timestamp()
        os.utime(stale_doc, (thirty_five_days_ago, thirty_five_days_ago))
        
        # ACT
        findings = agent._check_docs_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Stale Planning Document"
        assert findings[0].severity == Severity.LOW


class TestObsoleteFileDetection:
    """Test obsolete file pattern detection"""
    
    def test_detects_temp_prefix_files(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'temp_test.py').write_text('# temp\n')
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Obsolete File"
        assert findings[0].severity == Severity.MEDIUM
        assert "DELETE" in findings[0].recommendation
    
    def test_detects_old_prefix_files(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'old_version.py').write_text('# old\n')
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert "old_" in findings[0].description.lower()
    
    def test_detects_debug_prefix_files(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'debug_script.py').write_text('# debug\n')
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
    
    def test_detects_backup_suffix_files(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'config_backup.py').write_text('# backup\n')
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
    
    def test_detects_multiple_obsolete_patterns(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'temp_1.py').write_text('')
        (tmp_path / 'old_2.py').write_text('')
        (tmp_path / 'file.bak').write_text('')
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 3
    
    def test_skips_excluded_directories(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        git_dir = tmp_path / '.git'
        git_dir.mkdir()
        (git_dir / 'temp_file.py').write_text('')  # Should be ignored
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 0  # .git directory excluded


class TestModuleStructureValidation:
    """Test module directory structure validation"""
    
    def test_detects_loose_python_file_in_modules_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        modules_dir = tmp_path / 'modules'
        modules_dir.mkdir()
        (modules_dir / 'loose_file.py').write_text('# loose\n')
        
        # ACT
        findings = agent._check_modules_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert findings[0].category == "Module Structure Violation"
        assert findings[0].severity == Severity.MEDIUM
        assert "loose_file.py" in findings[0].description
    
    def test_allows_init_py_in_modules_root(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        modules_dir = tmp_path / 'modules'
        modules_dir.mkdir()
        (modules_dir / '__init__.py').write_text('# init\n')
        
        # ACT
        findings = agent._check_modules_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 0  # __init__.py is allowed
    
    def test_detects_missing_module_json(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        module_dir = tmp_path / 'modules' / 'test_module'
        module_dir.mkdir(parents=True)
        (module_dir / 'backend').mkdir()
        
        # ACT
        findings = agent._check_modules_directory(tmp_path)
        
        # ASSERT
        assert any(f.category == "Missing Module Configuration" for f in findings)
        missing_config = [f for f in findings if f.category == "Missing Module Configuration"][0]
        assert missing_config.severity == Severity.HIGH
        assert "module.json" in missing_config.recommendation
    
    def test_detects_missing_readme(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        module_dir = tmp_path / 'modules' / 'test_module'
        module_dir.mkdir(parents=True)
        (module_dir / 'module.json').write_text('{}')
        
        # ACT
        findings = agent._check_modules_directory(tmp_path)
        
        # ASSERT
        assert any(f.category == "Missing Module Documentation" for f in findings)
        missing_doc = [f for f in findings if f.category == "Missing Module Documentation"][0]
        assert missing_doc.severity == Severity.MEDIUM
        assert "README.md" in missing_doc.recommendation


class TestModuleAnalysis:
    """Test full module (project) analysis"""
    
    def test_analyzes_complete_project(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        
        # Create clean structure
        (tmp_path / 'README.md').write_text('# Project\n')
        modules_dir = tmp_path / 'modules'
        modules_dir.mkdir()
        (modules_dir / '__init__.py').write_text('')
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.agent_name == "file_organization"
        assert report.module_path == tmp_path
        assert report.metrics['files_scanned'] >= 2
    
    def test_handles_invalid_module_path(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        invalid_path = tmp_path / "nonexistent"
        
        # ACT
        report = agent.analyze_module(invalid_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "invalid" in report.summary.lower()
    
    def test_generates_clean_report_no_violations(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'README.md').write_text('# Clean\n')
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert len(report.findings) == 0
        assert "clean" in report.summary.lower()


class TestMetrics:
    """Test metrics calculation"""
    
    def test_metrics_count_findings_by_severity(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'temp_file.py').write_text('')  # MEDIUM
        (tmp_path / 'random.md').write_text('')  # HIGH
        modules_dir = tmp_path / 'modules' / 'test_mod'
        modules_dir.mkdir(parents=True)  # Missing module.json = HIGH
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.metrics['critical_count'] == 0
        assert report.metrics['high_count'] >= 1
        assert report.metrics['medium_count'] >= 1
    
    def test_metrics_count_files_scanned(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'file1.txt').write_text('')
        (tmp_path / 'file2.txt').write_text('')
        (tmp_path / 'file3.txt').write_text('')
        
        # ACT
        report = agent.analyze_module(tmp_path)
        
        # ASSERT
        assert report.metrics['files_scanned'] >= 3


class TestErrorHandling:
    """Test error handling"""
    
    def test_handles_permission_errors_gracefully(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        
        # ACT (even if directory has issues, should not crash)
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert isinstance(findings, list)


class TestRecommendations:
    """Test recommendation quality"""
    
    def test_markdown_recommendation_suggests_knowledge_vault(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'guide.md').write_text('# Guide\n')
        
        # ACT
        findings = agent._check_root_directory(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert "docs/knowledge/" in findings[0].recommendation
    
    def test_temp_file_recommendation_suggests_delete(self, tmp_path):
        # ARRANGE
        agent = FileOrganizationAgent()
        (tmp_path / 'temp_test.py').write_text('')
        
        # ACT
        findings = agent._check_obsolete_files(tmp_path)
        
        # ASSERT
        assert len(findings) == 1
        assert "DELETE" in findings[0].recommendation.upper()