"""
File Organization Agent - File Placement & Structure Analysis

Specializes in:
- Misplaced file detection (ALL directories, not just root)
- Obsolete file identification (temp files, old versions)
- Directory structure validation
- File naming convention compliance
- Cleanup recommendations

Based on: docs/knowledge/guidelines/feng-shui-phase5-file-organization.md
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime, timedelta
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class FileOrganizationAgent(BaseAgent):
    """
    Specializes in file placement and project structure
    
    Validates:
    - Files are in correct directories
    - No temporary/obsolete files lingering
    - Directory structure matches conventions
    - File naming follows patterns
    """
    
    def __init__(self):
        super().__init__("file_organization")
        
        # Allowed root-level files (from feng-shui-phase5)
        self.allowed_root_files = {
            '.clinerules', 'PROJECT_TRACKER.md', 'README.md', '.gitignore',
            'package.json', 'requirements.txt', 'setup.py', 'pyproject.toml',
            'pytest.ini', 'conftest.py', 'server.py', 'playwright.config.js',
            'feature_flags.json'
        }
        
        # Temporary/obsolete file patterns
        self.temp_patterns = [
            re.compile(r'^temp_.*\.py$'),
            re.compile(r'^old_.*\.py$'),
            re.compile(r'^debug_.*\.py$'),
            re.compile(r'.*_old\.py$'),
            re.compile(r'.*_backup\.py$'),
            re.compile(r'.*\.bak$'),
            re.compile(r'.*~$'),
            re.compile(r'.*_response\.json$'),
            re.compile(r'.*_output\.json$'),
        ]
        
        # File type to directory mappings
        self.file_type_rules = {
            '*.db': ['database/', 'app/database/'],
            '*.log': ['logs/', 'app/logs/'],
            'test_*.py': ['tests/', 'scripts/test/'],
            'check_*.py': ['scripts/test/'],
            'verify_*.py': ['scripts/test/'],
            'validate_*.py': ['scripts/test/'],
        }
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze entire project file organization
        
        Note: module_path is typically project root for this agent
        (unlike other agents that analyze per-module)
        
        Checks:
        - Root directory cleanliness
        - All directories for misplaced files
        - Obsolete files across project
        - Directory structure compliance
        
        Args:
            module_path: Path to project root
            
        Returns:
            AgentReport with file organization findings
        """
        start_time = time.time()
        findings = []
        
        if not self.validate_module_path(module_path):
            return AgentReport(
                agent_name=self.name,
                module_path=module_path,
                execution_time_seconds=0,
                findings=[],
                metrics={},
                summary="Invalid module path"
            )
        
        self.logger.info(f"Analyzing file organization of {module_path}")
        
        # Check root directory
        findings.extend(self._check_root_directory(module_path))
        
        # Check scripts/ hierarchy
        findings.extend(self._check_scripts_directory(module_path))
        
        # Check docs/ hierarchy
        findings.extend(self._check_docs_directory(module_path))
        
        # Check for obsolete files project-wide
        findings.extend(self._check_obsolete_files(module_path))
        
        # Check module structure
        findings.extend(self._check_modules_directory(module_path))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        total_files_scanned = sum(1 for _ in module_path.rglob('*') if _.is_file())
        
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'files_scanned': total_files_scanned
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"File organization analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of file organization capabilities"""
        return [
            "Root directory cleanliness validation",
            "Misplaced file detection (ALL directories)",
            "Obsolete/temporary file identification",
            "scripts/ hierarchy validation (python/, test/, tmp/, sql/)",
            "docs/ hierarchy validation (knowledge vault structure)",
            "Module structure compliance checking",
            "File naming convention validation",
            "Cleanup recommendations with safe actions"
        ]
    
    def _check_root_directory(self, project_root: Path) -> List[Finding]:
        """
        Check root directory for unauthorized files
        
        Based on feng-shui-phase5 guidelines:
        - Only essential entry points and configs allowed
        - No test outputs, temp files, databases, logs
        """
        findings = []
        
        try:
            for item in project_root.iterdir():
                if not item.is_file():
                    continue
                
                filename = item.name
                
                # Skip hidden files (., ..)
                if filename.startswith('.') and filename not in self.allowed_root_files:
                    continue
                
                # Check if file is allowed
                if filename not in self.allowed_root_files:
                    # Determine severity and recommendation based on file type
                    if filename.endswith('.md'):
                        severity = Severity.HIGH
                        recommendation = "Move to docs/knowledge/ (knowledge vault) or delete if obsolete"
                    elif filename.endswith('.db'):
                        severity = Severity.HIGH
                        recommendation = "Move to app/database/ or add to .gitignore"
                    elif filename.endswith('.log'):
                        severity = Severity.MEDIUM
                        recommendation = "Move to logs/ or delete"
                    elif filename.startswith('temp_') or filename.startswith('old_'):
                        severity = Severity.MEDIUM
                        recommendation = "DELETE (temporary/obsolete file)"
                    elif filename.endswith(('.json', '.yaml', '.yml')) and 'env' in filename.lower():
                        severity = Severity.HIGH
                        recommendation = "Move to app/ or add to .gitignore"
                    elif filename.startswith('test_'):
                        severity = Severity.MEDIUM
                        recommendation = "Move to tests/ or scripts/test/"
                    else:
                        severity = Severity.LOW
                        recommendation = "Review if file belongs in root or should be relocated"
                    
                    findings.append(Finding(
                        category="Root Directory Clutter",
                        severity=severity,
                        file_path=item,
                        line_number=None,
                        description=f"Unauthorized file in root directory: {filename}",
                        recommendation=recommendation,
                        code_snippet=None
                    ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze root directory: {str(e)}")
        
        return findings
    
    def _check_scripts_directory(self, project_root: Path) -> List[Finding]:
        """
        Check scripts/ hierarchy
        
        Rules:
        - scripts/python/: Reusable utilities (create_*, populate_*, migrate_*)
        - scripts/test/: Test/validation scripts (test_*, check_*, verify_*)
        - scripts/tmp/: One-shot scripts (<7 days old)
        - scripts/sql/: SQL scripts
        """
        findings = []
        scripts_dir = project_root / 'scripts'
        
        if not scripts_dir.exists():
            return findings
        
        try:
            # Check scripts/python/ for test files (should be in scripts/test/)
            python_dir = scripts_dir / 'python'
            if python_dir.exists():
                for py_file in python_dir.rglob('*.py'):
                    filename = py_file.name
                    if (filename.startswith('test_') or filename.startswith('check_') or 
                        filename.startswith('verify_') or filename.startswith('validate_')):
                        findings.append(Finding(
                            category="Misplaced Script",
                            severity=Severity.MEDIUM,
                            file_path=py_file,
                            line_number=None,
                            description=f"Test/validation script in wrong location: {filename}",
                            recommendation="Move to scripts/test/ or tests/integration/",
                            code_snippet=None
                        ))
            
            # Check scripts/tmp/ for old files (>7 days)
            tmp_dir = scripts_dir / 'tmp'
            if tmp_dir.exists():
                seven_days_ago = datetime.now() - timedelta(days=7)
                for tmp_file in tmp_dir.rglob('*'):
                    if not tmp_file.is_file():
                        continue
                    
                    mtime = datetime.fromtimestamp(tmp_file.stat().st_mtime)
                    if mtime < seven_days_ago:
                        findings.append(Finding(
                            category="Obsolete Temporary File",
                            severity=Severity.LOW,
                            file_path=tmp_file,
                            line_number=None,
                            description=f"Temporary file older than 7 days: {tmp_file.name}",
                            recommendation="DELETE (one-shot scripts should be short-lived)",
                            code_snippet=None
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze scripts directory: {str(e)}")
        
        return findings
    
    def _check_docs_directory(self, project_root: Path) -> List[Finding]:
        """
        Check docs/ hierarchy
        
        Rules:
        - docs/knowledge/: Knowledge vault (architecture/, guides/, etc.)
        - docs/archive/: Archived documentation
        - docs/planning/: Active planning (should be reviewed periodically)
        - No .md files directly in docs/ root
        """
        findings = []
        docs_dir = project_root / 'docs'
        
        if not docs_dir.exists():
            return findings
        
        try:
            # Check for .md files directly in docs/ root (should be in subdirectories)
            for md_file in docs_dir.glob('*.md'):
                # Allow specific audit/requirement docs in docs/ root
                if md_file.name not in ['FENG_SHUI_AUDIT_2026-02-01.md', 
                                        'FENG_SHUI_AUDIT_2026-02-05.md',
                                        'FENG_SHUI_ROUTINE_REQUIREMENTS.md',
                                        'PYTHON_MIGRATION_PLAN.md']:
                    findings.append(Finding(
                        category="Documentation Misplacement",
                        severity=Severity.MEDIUM,
                        file_path=md_file,
                        line_number=None,
                        description=f"Markdown file in docs/ root: {md_file.name}",
                        recommendation="Move to docs/knowledge/ subdirectory (architecture/, guides/, guidelines/, etc.)",
                        code_snippet=None
                    ))
            
            # Check docs/planning/ for stale planning docs (>30 days)
            planning_dir = docs_dir / 'planning'
            if planning_dir.exists():
                thirty_days_ago = datetime.now() - timedelta(days=30)
                for planning_file in planning_dir.rglob('*.md'):
                    mtime = datetime.fromtimestamp(planning_file.stat().st_mtime)
                    if mtime < thirty_days_ago:
                        findings.append(Finding(
                            category="Stale Planning Document",
                            severity=Severity.LOW,
                            file_path=planning_file,
                            line_number=None,
                            description=f"Planning doc older than 30 days: {planning_file.name}",
                            recommendation="Review: Is this still active planning? If implemented, move to docs/knowledge/ or archive.",
                            code_snippet=None
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze docs directory: {str(e)}")
        
        return findings
    
    def _check_obsolete_files(self, project_root: Path) -> List[Finding]:
        """
        Check entire project for temporary/obsolete files
        
        Detects:
        - temp_*.py, old_*.py, debug_*.py files
        - *_backup.py, *.bak files
        - *_response.json, *_output.json (test outputs)
        - Files with ~ suffix (editor backups)
        """
        findings = []
        
        try:
            # Scan entire project (excluding .git, node_modules, venv, etc.)
            exclude_dirs = {'.git', 'node_modules', 'venv', '__pycache__', '.pytest_cache', 
                           'htmlcov', 'test-results', 'steel_thread_on_sap.egg-info'}
            
            for root, dirs, files in os.walk(project_root):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for filename in files:
                    file_path = Path(root) / filename
                    
                    # Check against temporary patterns
                    for pattern in self.temp_patterns:
                        if pattern.match(filename):
                            findings.append(Finding(
                                category="Obsolete File",
                                severity=Severity.MEDIUM,
                                file_path=file_path,
                                line_number=None,
                                description=f"Temporary/obsolete file: {filename}",
                                recommendation="DELETE (temporary files should not be committed)",
                                code_snippet=None
                            ))
                            break  # One finding per file
        
        except Exception as e:
            self.logger.warning(f"Could not scan for obsolete files: {str(e)}")
        
        return findings
    
    def _check_modules_directory(self, project_root: Path) -> List[Finding]:
        """
        Check modules/ structure
        
        Rules:
        - Each module should have: module.json, backend/, README.md
        - No loose .py files in modules/ root
        - Tests should be in module's tests/ subdirectory
        """
        findings = []
        modules_dir = project_root / 'modules'
        
        if not modules_dir.exists():
            return findings
        
        try:
            # Check for loose Python files in modules/ root
            for py_file in modules_dir.glob('*.py'):
                if py_file.name != '__init__.py':
                    findings.append(Finding(
                        category="Module Structure Violation",
                        severity=Severity.MEDIUM,
                        file_path=py_file,
                        line_number=None,
                        description=f"Loose Python file in modules/ root: {py_file.name}",
                        recommendation="Move to appropriate module subdirectory (backend/, tests/) or core/services/",
                        code_snippet=None
                    ))
            
            # Check each module for required structure
            for module_dir in modules_dir.iterdir():
                if not module_dir.is_dir() or module_dir.name == '__pycache__':
                    continue
                
                # Check for module.json
                if not (module_dir / 'module.json').exists():
                    findings.append(Finding(
                        category="Missing Module Configuration",
                        severity=Severity.HIGH,
                        file_path=module_dir,
                        line_number=None,
                        description=f"Module missing module.json: {module_dir.name}",
                        recommendation="Create module.json with module metadata and feature flag",
                        code_snippet=None
                    ))
                
                # Check for README.md
                if not (module_dir / 'README.md').exists():
                    findings.append(Finding(
                        category="Missing Module Documentation",
                        severity=Severity.MEDIUM,
                        file_path=module_dir,
                        line_number=None,
                        description=f"Module missing README.md: {module_dir.name}",
                        recommendation="Create README.md documenting module purpose, API, and usage",
                        code_snippet=None
                    ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze modules directory: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"File organization validated: {metrics['files_scanned']} files scanned, structure is clean"
        
        return (
            f"FILE ORGANIZATION ISSUES: "
            f"{metrics['total_findings']} misplaced/obsolete files found "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM) "
            f"in {metrics['files_scanned']} scanned files"
        )