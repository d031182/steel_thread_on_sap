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
        
        # NEW: Check for directory duplication patterns
        findings.extend(self._check_directory_duplication(module_path))
        
        # NEW: Check for stale backup directories (v4.12)
        findings.extend(self._check_backup_directories(module_path))
        
        # NEW: Check for coverage artifacts in root (v4.12)
        findings.extend(self._check_coverage_artifacts(module_path))
        
        # NEW: Check for duplicate pytest/test configuration files (v4.12)
        findings.extend(self._check_duplicate_test_configs(module_path))
        
        # NEW: Check for misplaced utility/test scripts in root (v4.12)
        findings.extend(self._check_utility_test_scripts(module_path))
        
        # NEW: Check for scattered documentation (v4.31 - Shi Fu Enhancement 20260212-FILE-scattered_)
        findings.extend(self._detect_scattered_documentation(module_path))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics (with safety limit to prevent infinite loops)
        MAX_FILES_TO_SCAN = 10000  # Safety limit
        total_files_scanned = 0
        try:
            for _ in module_path.rglob('*'):
                if _.is_file():
                    total_files_scanned += 1
                    if total_files_scanned >= MAX_FILES_TO_SCAN:
                        self.logger.warning(f"Hit max file scan limit ({MAX_FILES_TO_SCAN}), stopping count")
                        break
        except Exception as e:
            self.logger.warning(f"Error counting files: {str(e)}")
        
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
            "Directory duplication detection (catches /sql vs /scripts/sql patterns)",
            "Consolidation recommendations for duplicate directories",
            "Stale backup directory detection (v4.12 - age-based with patterns)",
            "Test artifact validation (v4.12 - pytest + Playwright outputs)",
            "Duplicate test configuration detection (v4.12 - conftest.py, pytest.ini)",
            "Utility/test script detection (v4.12 - test_*, check_*, run_* in root)",
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
            
            # Safety limits to prevent infinite loops
            MAX_FILES_TO_CHECK = 5000
            files_checked = 0
            
            for root, dirs, files in os.walk(project_root, followlinks=False):  # Don't follow symlinks
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                # Safety check: Stop if we've checked too many files
                if files_checked >= MAX_FILES_TO_CHECK:
                    self.logger.warning(f"Hit max obsolete file check limit ({MAX_FILES_TO_CHECK}), stopping scan")
                    break
                
                for filename in files:
                    files_checked += 1
                    
                    # Safety check within inner loop too
                    if files_checked >= MAX_FILES_TO_CHECK:
                        break
                    
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
    
    def _check_directory_duplication(self, project_root: Path) -> List[Finding]:
        """
        Check for directory duplication patterns
        
        Detects scenarios like:
        - /sql/ and /scripts/sql/ (should consolidate to /scripts/sql/)
        - /docs/something/ and /something/ (should be in /docs/)
        - Similar directory names in different locations
        
        This addresses the gap where user found /sql/sqlite/ duplicated 
        with /scripts/sql/sqlite/ that wasn't caught by other checks.
        """
        findings = []
        
        try:
            # Define known consolidation patterns
            # Format: (pattern_dir, canonical_dir, description)
            consolidation_patterns = [
                # SQL scripts should be in /scripts/sql/
                ('sql', 'scripts/sql', 'SQL scripts'),
                # Python utilities should be in /scripts/python/
                ('scripts_old', 'scripts/python', 'Python utility scripts'),
                # Test scripts should be in /scripts/test/ or /tests/
                ('test_scripts', 'scripts/test', 'Test/validation scripts'),
                # Docs should be in /docs/
                ('documentation', 'docs/knowledge', 'Documentation'),
            ]
            
            # Check each consolidation pattern
            for pattern_dir, canonical_dir, desc in consolidation_patterns:
                pattern_path = project_root / pattern_dir
                canonical_path = project_root / canonical_dir
                
                # If pattern directory exists and canonical also exists, flag for consolidation
                if pattern_path.exists() and canonical_path.exists():
                    findings.append(Finding(
                        category="Directory Duplication",
                        severity=Severity.HIGH,
                        file_path=pattern_path,
                        line_number=None,
                        description=f"Duplicate directory detected: {pattern_dir}/ exists alongside {canonical_dir}/",
                        recommendation=f"CONSOLIDATE: Move contents of {pattern_dir}/ to {canonical_dir}/ to eliminate duplication. {desc} should have single canonical location.",
                        code_snippet=None
                    ))
            
            # Advanced: Check for similar subdirectory names across different parent dirs
            # This catches patterns like /sql/sqlite/ vs /scripts/sql/sqlite/
            dir_index: Dict[str, List[Path]] = {}
            
            # Build index of directory names
            exclude_dirs = {'.git', 'node_modules', 'venv', '__pycache__', 
                           '.pytest_cache', 'htmlcov', 'test-results', 
                           'steel_thread_on_sap.egg-info', 'database', 'logs'}
            
            MAX_DIRS_TO_SCAN = 1000  # Safety limit
            dirs_scanned = 0
            
            for root, dirs, _ in os.walk(project_root, followlinks=False):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                # Safety check
                if dirs_scanned >= MAX_DIRS_TO_SCAN:
                    self.logger.warning(f"Hit max directory scan limit ({MAX_DIRS_TO_SCAN}), stopping duplication check")
                    break
                
                for dirname in dirs:
                    dirs_scanned += 1
                    if dirs_scanned >= MAX_DIRS_TO_SCAN:
                        break
                    
                    # Special case: Look for similar paths (e.g., sql/sqlite vs scripts/sql/sqlite)
                    dir_path = Path(root) / dirname
                    relative = dir_path.relative_to(project_root)
                    
                    # Check if this directory name appears in multiple locations
                    if dirname not in dir_index:
                        dir_index[dirname] = []
                    dir_index[dirname].append(relative)
            
            # Analyze for duplicates
            for dirname, locations in dir_index.items():
                if len(locations) > 1:
                    # Check if these are semantically similar (e.g., both contain SQL files)
                    # For now, flag if same subdirectory name appears in multiple places
                    # and at least one is in a "canonical" location like scripts/
                    
                    canonical_locs = [loc for loc in locations if 'scripts' in str(loc)]
                    other_locs = [loc for loc in locations if 'scripts' not in str(loc)]
                    
                    if canonical_locs and other_locs:
                        for other_loc in other_locs:
                            # Check if both directories contain similar file types
                            if self._directories_have_similar_content(
                                project_root / other_loc, 
                                project_root / canonical_locs[0]
                            ):
                                findings.append(Finding(
                                    category="Potential Directory Duplication",
                                    severity=Severity.MEDIUM,
                                    file_path=project_root / other_loc,
                                    line_number=None,
                                    description=f"Subdirectory '{dirname}' appears in multiple locations: {other_loc} and {canonical_locs[0]}",
                                    recommendation=f"REVIEW: Check if {other_loc} duplicates {canonical_locs[0]}. If so, consolidate to {canonical_locs[0]}.",
                                    code_snippet=None
                                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check directory duplication: {str(e)}")
        
        return findings
    
    def _directories_have_similar_content(self, dir1: Path, dir2: Path) -> bool:
        """
        Check if two directories contain similar file types
        
        Used to determine if directories are likely duplicates
        Returns True if >50% of file extensions match
        """
        try:
            if not dir1.exists() or not dir2.exists():
                return False
            
            # Get file extensions from both directories
            ext1 = {f.suffix for f in dir1.rglob('*') if f.is_file()}
            ext2 = {f.suffix for f in dir2.rglob('*') if f.is_file()}
            
            if not ext1 or not ext2:
                return False
            
            # Calculate similarity (intersection / union)
            intersection = len(ext1 & ext2)
            union = len(ext1 | ext2)
            
            similarity = intersection / union if union > 0 else 0
            
            return similarity > 0.5  # 50% threshold
        
        except Exception:
            return False
    
    def _check_backup_directories(self, project_root: Path) -> List[Finding]:
        """
        Detect stale backup directories (NEW in v4.12)
        
        Detects backup directories that are > 30 days old and causing confusion.
        This addresses the gap where user found database_cleanup_backup_20260205/
        (1 month old) that wasn't caught by other checks.
        
        Patterns detected:
        - *_backup_YYYYMMDD/ (date-stamped backups)
        - *_old/ (directories marked as old)
        - *_legacy/ (legacy versions)
        - database_cleanup_* (specific cleanup patterns)
        
        Args:
            project_root: Path to project root
            
        Returns:
            List of findings for stale backup directories
        """
        findings = []
        
        try:
            # Backup directory patterns
            backup_patterns = [
                (re.compile(r'.*_backup_\d{8}'), 30),  # _backup_20260205 (30 days)
                (re.compile(r'.*_old'), 14),           # *_old (14 days)
                (re.compile(r'.*_legacy'), 90),        # *_legacy (90 days)
                (re.compile(r'database_cleanup.*'), 30),  # database_cleanup_* (30 days)
            ]
            
            for item in project_root.iterdir():
                if not item.is_dir():
                    continue
                
                # Check against backup patterns
                for pattern, age_threshold_days in backup_patterns:
                    if pattern.match(item.name):
                        # Get directory age
                        try:
                            mtime = datetime.fromtimestamp(item.stat().st_mtime)
                            age_days = (datetime.now() - mtime).days
                            
                            if age_days > age_threshold_days:
                                # Count files in directory (for context)
                                file_count = sum(1 for _ in item.rglob('*') if _.is_file())
                                
                                findings.append(Finding(
                                    category="Stale Backup Directory",
                                    severity=Severity.HIGH,
                                    file_path=item,
                                    line_number=None,
                                    description=f"Backup directory {age_days} days old (>{age_threshold_days} days): {item.name} ({file_count} files)",
                                    recommendation=f"DELETE if no longer needed. Backup directories > {age_threshold_days} days old cause confusion (user feedback: 'wasted my time')",
                                    code_snippet=None
                                ))
                                break  # One finding per directory
                        
                        except Exception as e:
                            self.logger.warning(f"Could not check age of {item.name}: {str(e)}")
        
        except Exception as e:
            self.logger.warning(f"Could not check backup directories: {str(e)}")
        
        return findings
    
    def _check_coverage_artifacts(self, project_root: Path) -> List[Finding]:
        """
        Detect test artifacts in root directory (NEW in v4.12)
        
        Test outputs (coverage, Playwright results) should be in tests/ directory, not project root.
        This addresses the gap where user found coverage.xml and test-results/ in root.
        
        Detects:
        - coverage.xml (pytest-cov XML report)
        - .coverage (pytest-cov SQLite database)
        - htmlcov/ (pytest-cov HTML reports)
        - test-results/ (Playwright E2E test results)
        
        Args:
            project_root: Path to project root
            
        Returns:
            List of findings for misplaced test artifacts
        """
        findings = []
        
        try:
            # pytest coverage artifacts that should be in tests/
            coverage_files = [
                ('coverage.xml', 'tests/coverage.xml', 'pytest.ini: --cov-report=xml:tests/coverage.xml'),
                ('.coverage', 'tests/.coverage', 'pytest.ini: --cov-report paths'),
            ]
            
            for filename, correct_location, config_hint in coverage_files:
                artifact_path = project_root / filename
                
                if artifact_path.exists():
                    findings.append(Finding(
                        category="Misplaced Test Artifact",
                        severity=Severity.MEDIUM,
                        file_path=artifact_path,
                        line_number=None,
                        description=f"pytest coverage artifact in root directory: {filename}",
                        recommendation=f"MOVE to {correct_location}. Configure {config_hint}",
                        code_snippet=None
                    ))
            
            # pytest HTML coverage reports
            htmlcov_path = project_root / 'htmlcov'
            if htmlcov_path.exists() and htmlcov_path.is_dir():
                file_count = sum(1 for _ in htmlcov_path.rglob('*') if _.is_file())
                findings.append(Finding(
                    category="Misplaced Test Artifact",
                    severity=Severity.HIGH,
                    file_path=htmlcov_path,
                    line_number=None,
                    description=f"pytest HTML coverage reports in root directory: htmlcov/ ({file_count} files)",
                    recommendation="MOVE to tests/htmlcov/. Configure pytest.ini: --cov-report=html:tests/htmlcov. Add htmlcov/ to .gitignore.",
                    code_snippet=None
                ))
            
            # Playwright E2E test results
            playwright_results_path = project_root / 'test-results'
            if playwright_results_path.exists() and playwright_results_path.is_dir():
                file_count = sum(1 for _ in playwright_results_path.rglob('*') if _.is_file())
                findings.append(Finding(
                    category="Misplaced Test Artifact",
                    severity=Severity.HIGH,
                    file_path=playwright_results_path,
                    line_number=None,
                    description=f"Playwright E2E test results in root directory: test-results/ ({file_count} files)",
                    recommendation="MOVE to tests/playwright-results/. Configure playwright.config.js: outputDir: './tests/playwright-results'. Add test-results/ to .gitignore.",
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check test artifacts: {str(e)}")
        
        return findings
    
    def _check_duplicate_test_configs(self, project_root: Path) -> List[Finding]:
        """
        Detect duplicate pytest/test configuration files (NEW in v4.12)
        
        Detects when test configuration files exist in both root and tests/,
        causing duplication and confusion about which is authoritative.
        
        This addresses Issue #8 where user found:
        - Root-level conftest.py (8 lines, minimal path setup)
        - tests/conftest.py (160 lines, comprehensive with Gu Wu)
        Both doing the SAME path setup → redundant!
        
        Pytest behavior:
        - pytest loads conftest.py files hierarchically
        - Root-level conftest.py loaded FIRST (if exists)
        - tests/conftest.py loaded for tests in tests/
        - If tests/conftest.py does EVERYTHING, root-level is redundant
        
        Detects:
        - conftest.py in root when tests/conftest.py exists
        - pytest.ini duplication (root vs tests/)
        - tox.ini duplication (root vs tests/)
        
        Args:
            project_root: Path to project root
            
        Returns:
            List of findings for duplicate test configuration files
        """
        findings = []
        
        try:
            # Check for duplicate conftest.py
            root_conftest = project_root / 'conftest.py'
            tests_conftest = project_root / 'tests' / 'conftest.py'
            
            if root_conftest.exists() and tests_conftest.exists():
                # Read both files to compare
                try:
                    root_content = root_conftest.read_text(encoding='utf-8')
                    tests_content = tests_conftest.read_text(encoding='utf-8')
                    
                    # Check if root conftest is minimal (< 50 lines) and tests/ is comprehensive
                    root_lines = len(root_content.splitlines())
                    tests_lines = len(tests_content.splitlines())
                    
                    # Check if both do path setup (common duplication)
                    has_path_setup_root = 'sys.path' in root_content
                    has_path_setup_tests = 'sys.path' in tests_content
                    
                    if tests_lines > root_lines * 5:  # tests/ is >5x longer
                        findings.append(Finding(
                            category="Duplicate Test Configuration",
                            severity=Severity.HIGH,
                            file_path=root_conftest,
                            line_number=None,
                            description=f"Redundant root-level conftest.py ({root_lines} lines) when tests/conftest.py ({tests_lines} lines) is comprehensive",
                            recommendation="DELETE root-level conftest.py. Keep tests/conftest.py as single source of truth for pytest configuration.",
                            code_snippet=None
                        ))
                    elif has_path_setup_root and has_path_setup_tests:
                        findings.append(Finding(
                            category="Duplicate Test Configuration",
                            severity=Severity.MEDIUM,
                            file_path=root_conftest,
                            line_number=None,
                            description=f"Both conftest.py files do path setup (duplication)",
                            recommendation="CONSOLIDATE: Move all pytest config to tests/conftest.py, delete root-level if redundant",
                            code_snippet=None
                        ))
                
                except Exception as e:
                    self.logger.warning(f"Could not compare conftest.py files: {str(e)}")
            
            # Check for duplicate pytest.ini (less common but possible)
            root_pytest_ini = project_root / 'pytest.ini'
            tests_pytest_ini = project_root / 'tests' / 'pytest.ini'
            
            if root_pytest_ini.exists() and tests_pytest_ini.exists():
                findings.append(Finding(
                    category="Duplicate Test Configuration",
                    severity=Severity.HIGH,
                    file_path=tests_pytest_ini,
                    line_number=None,
                    description="Duplicate pytest.ini files (root and tests/)",
                    recommendation="CONSOLIDATE: Keep root-level pytest.ini only (pytest loads from root by default)",
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check duplicate test configs: {str(e)}")
        
        return findings
    
    def _check_utility_test_scripts(self, project_root: Path) -> List[Finding]:
        """
        Detect misplaced utility/test scripts in root (NEW in v4.12)
        
        Test, validation, and utility scripts belong in scripts/test/, not root.
        This addresses Issues #9-11 where user found:
        - run_fengshui_analysis.py (utility script)
        - test_ai_assistant_query.py (test script)
        - check_databases.py (validation script)
        
        All should be in scripts/test/ for consolidation and organization.
        
        Detects patterns in root:
        - test_*.py → scripts/test/
        - check_*.py → scripts/test/
        - verify_*.py → scripts/test/
        - validate_*.py → scripts/test/
        - run_*.py (utilities) → scripts/test/ or scripts/python/
        
        Args:
            project_root: Path to project root
            
        Returns:
            List of findings for misplaced utility/test scripts
        """
        findings = []
        
        try:
            # Utility/test script patterns
            utility_patterns = [
                (re.compile(r'^test_.*\.py$'), 'scripts/test/', 'Test script'),
                (re.compile(r'^check_.*\.py$'), 'scripts/test/', 'Validation script'),
                (re.compile(r'^verify_.*\.py$'), 'scripts/test/', 'Verification script'),
                (re.compile(r'^validate_.*\.py$'), 'scripts/test/', 'Validation script'),
                (re.compile(r'^run_.*\.py$'), 'scripts/test/', 'Utility script'),
            ]
            
            # Check root directory for utility/test scripts
            for item in project_root.glob('*.py'):
                if not item.is_file():
                    continue
                
                filename = item.name
                
                # Check against utility patterns
                for pattern, target_dir, desc in utility_patterns:
                    if pattern.match(filename):
                        findings.append(Finding(
                            category="Misplaced Utility Script",
                            severity=Severity.MEDIUM,
                            file_path=item,
                            line_number=None,
                            description=f"{desc} in root directory: {filename}",
                            recommendation=f"MOVE to {target_dir}. {desc}s belong in scripts/test/ for consolidation.",
                            code_snippet=None
                        ))
                        break  # One finding per file
        
        except Exception as e:
            self.logger.warning(f"Could not check utility/test scripts: {str(e)}")
        
        return findings
    
    def _detect_scattered_documentation(self, project_root: Path) -> List[Finding]:
        """
        Detect scattered documentation that should be consolidated (NEW - Shi Fu Enhancement)
        
        Detects documentation sprawl patterns:
        - Multiple docs about same topic in different directories
        - Docs outside knowledge vault structure (docs/knowledge/)
        - Naming patterns suggesting related docs (e.g., "feng-shui-*", "gu-wu-*")
        - Docs in root when they should be in docs/knowledge/
        
        This implements Shi Fu Enhancement Proposal 20260212-FILE-scattered_
        User insight: "Feng Shui could also cover the consolidation of scattered documentations"
        
        Args:
            project_root: Path to project root
            
        Returns:
            List of findings for scattered documentation
        """
        findings = []
        
        try:
            # Define topic patterns that suggest related documentation
            topic_patterns = [
                ('feng-shui', 'quality-ecosystem/feng-shui/', 'Feng Shui'),
                ('fengshui', 'quality-ecosystem/feng-shui/', 'Feng Shui'),
                ('gu-wu', 'quality-ecosystem/gu-wu/', 'Gu Wu'),
                ('guwu', 'quality-ecosystem/gu-wu/', 'Gu Wu'),
                ('shi-fu', 'quality-ecosystem/shi-fu/', 'Shi Fu'),
                ('shifu', 'quality-ecosystem/shi-fu/', 'Shi Fu'),
                ('testing', 'quality-ecosystem/gu-wu/', 'Testing'),
                ('architecture', 'architecture/', 'Architecture'),
                ('knowledge-graph', 'knowledge-graph/', 'Knowledge Graph'),
                ('data-products', 'data-products/', 'Data Products'),
            ]
            
            # Canonical location for knowledge vault
            knowledge_vault = project_root / 'docs' / 'knowledge'
            
            # Build index of documentation files by topic
            doc_index: Dict[str, List[tuple]] = {pattern: [] for pattern, _, _ in topic_patterns}
            
            # Scan docs/knowledge/ for existing .md files
            if knowledge_vault.exists():
                MAX_DOCS_TO_SCAN = 500  # Safety limit
                docs_scanned = 0
                
                for md_file in knowledge_vault.rglob('*.md'):
                    docs_scanned += 1
                    if docs_scanned >= MAX_DOCS_TO_SCAN:
                        self.logger.warning(f"Hit max doc scan limit ({MAX_DOCS_TO_SCAN}), stopping")
                        break
                    
                    filename_lower = md_file.name.lower()
                    relative_path = md_file.relative_to(knowledge_vault)
                    
                    # Check which topic this doc relates to
                    for pattern, target_subdir, topic_name in topic_patterns:
                        if pattern in filename_lower:
                            doc_index[pattern].append((md_file, relative_path, topic_name))
            
            # Now check for scattered docs (same pattern in wrong locations)
            for pattern, target_subdir, topic_name in topic_patterns:
                # Check if multiple docs with same pattern exist in different locations
                locations_found = set()
                
                for md_file, relative_path, _ in doc_index[pattern]:
                    # Get parent directory relative to knowledge vault
                    parent_dir = str(relative_path.parent)
                    locations_found.add(parent_dir)
                
                # If same pattern appears in 2+ different subdirectories
                if len(locations_found) >= 2:
                    # Get all docs with this pattern
                    scattered_docs = doc_index[pattern]
                    
                    # Check if any are outside the target subdirectory
                    docs_outside_target = [
                        (doc, rel) for doc, rel, _ in scattered_docs 
                        if not str(rel).startswith(target_subdir.replace('/', os.sep))
                    ]
                    
                    if docs_outside_target:
                        # Create finding for the scattered pattern
                        doc_list = ', '.join([doc.name for doc, _ in docs_outside_target[:5]])
                        if len(docs_outside_target) > 5:
                            doc_list += f" (+{len(docs_outside_target) - 5} more)"
                        
                        findings.append(Finding(
                            category="Scattered Documentation",
                            severity=Severity.MEDIUM,
                            file_path=docs_outside_target[0][0].parent,  # Parent directory of first scattered doc
                            line_number=None,
                            description=f"Scattered {topic_name} documentation: {len(docs_outside_target)} docs in multiple locations instead of {target_subdir}",
                            recommendation=f"CONSOLIDATE: Move {topic_name} docs to docs/knowledge/{target_subdir}. Found: {doc_list}",
                            code_snippet=None
                        ))
            
            # Also check for .md files in root directory (should be in docs/)
            for md_file in project_root.glob('*.md'):
                filename = md_file.name
                # Allow specific root-level docs
                if filename not in {'.clinerules', 'PROJECT_TRACKER.md', 'README.md'}:
                    findings.append(Finding(
                        category="Scattered Documentation",
                        severity=Severity.HIGH,
                        file_path=md_file,
                        line_number=None,
                        description=f"Documentation file in root directory: {filename}",
                        recommendation="MOVE to docs/knowledge/ subdirectory (architecture/, guides/, etc.) or archive if obsolete",
                        code_snippet=None
                    ))
        
        except Exception as e:
            self.logger.warning(f"Could not check scattered documentation: {str(e)}")
        
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
