"""
Architect Agent - Architecture Patterns & Design Analysis

Specializes in:
- GoF pattern violations
- SOLID principle compliance
- DI violations (.connection, .service, .db_path access)
- Coupling/cohesion metrics
- Architecture pattern adherence
"""

import ast
import logging
from pathlib import Path
from typing import List, Dict, Optional
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity

# Log Intelligence (optional)
try:
    from core.interfaces.log_intelligence import LogAdapterInterface
except ImportError:
    LogAdapterInterface = None


class ArchitectAgent(BaseAgent):
    """
    Specializes in architecture quality analysis
    
    Detects:
    - Dependency Injection (DI) violations (static + runtime)
    - SOLID principle violations (primarily SRP, DIP)
    - High coupling/low cohesion issues
    - Architecture pattern violations
    
    Enhanced with optional log intelligence for runtime violation detection.
    """
    
    def __init__(self, log_adapter: Optional['LogAdapterInterface'] = None):
        """
        Initialize ArchitectAgent with optional log intelligence
        
        Args:
            log_adapter: Optional log adapter for runtime analysis.
                        If provided and available, enhances DI violation detection
                        with runtime error patterns from logs.
        """
        super().__init__("architect")
        self.log_adapter = log_adapter
        self.pattern_detectors = {
            'di_violation': self._detect_di_violations,
            'di_runtime': self._detect_di_violations_runtime,  # NEW: Runtime detection
            'solid_violation': self._detect_solid_violations,
            'large_classes': self._detect_large_classes,
            'repository_pattern': self._detect_repository_violations,  # NEW: Repository Pattern
            'facade_pattern': self._detect_facade_pattern_violations,  # NEW: Facade Pattern (v4.9)
            'backend_structure': self._detect_backend_structure_violations,  # NEW: Backend Structure (v4.9)
            'unit_of_work': self._detect_unit_of_work_violations,  # NEW: Unit of Work Pattern
            'service_layer': self._detect_service_layer_violations,  # NEW: Service Layer Pattern
        }
        
        # Log availability status
        if self.log_adapter and self.log_adapter.is_available():
            self.logger.info("Log intelligence enabled for runtime DI detection")
        else:
            self.logger.debug("Log intelligence not available (static analysis only)")
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module architecture
        
        Checks:
        - DI violations (.connection, .service, .db_path direct access)
        - SOLID principles (especially SRP via class size)
        - Large classes (>500 LOC → SRP violation)
        - Architecture pattern adherence
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with architecture findings
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
        
        self.logger.info(f"Analyzing architecture of {module_path}")
        
        # Run all detectors
        for detector_name, detector_func in self.pattern_detectors.items():
            try:
                detector_findings = detector_func(module_path)
                findings.extend(detector_findings)
                self.logger.debug(f"Detector '{detector_name}' found {len(detector_findings)} issues")
            except Exception as e:
                self.logger.error(f"Detector '{detector_name}' failed: {str(e)}")
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        python_files = list(module_path.rglob('*.py'))
        metrics = {
            'total_violations': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'files_analyzed': len(python_files)
        }
        
        # Generate summary
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"Architecture analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of architecture analysis capabilities"""
        capabilities = [
            "Dependency Injection (DI) violation detection (static)",
            "SOLID principle compliance checking (SRP focus)",
            "Large class detection (>500 LOC)",
            "Repository Pattern violation detection (v3.0.0)",
            "Facade Pattern violation detection (v4.9) ⭐ NEW",
            "Backend Structure validation (v4.9) ⭐ NEW",
            "Unit of Work Pattern violation detection (v4.7)",
            "Service Layer Pattern violation detection (v4.7)",
            "Architecture pattern adherence validation",
            "Coupling analysis (future)",
            "Cohesion analysis (future)"
        ]
        
        # Add runtime capability if logs available
        if self.log_adapter and self.log_adapter.is_available():
            capabilities.insert(1, "DI violation detection (runtime from logs)")
        
        return capabilities
    
    def _detect_di_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect direct dependency access (DI violations)
        
        Looks for:
        - .connection attribute access
        - .service attribute access  
        - .db_path attribute access
        
        These indicate hardcoded dependencies instead of DI.
        """
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            # Skip files in tests/ directories (but not files with 'test' in name elsewhere)
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content, filename=str(py_file))
                
                # Look for .connection, .service, .db_path access
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute):
                        if node.attr in ['connection', 'service', 'db_path']:
                            # Get surrounding context for snippet
                            lines = content.split('\n')
                            line_num = node.lineno
                            snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                            
                            findings.append(Finding(
                                category="DI Violation",
                                severity=Severity.HIGH,
                                file_path=py_file,
                                line_number=line_num,
                                description=f"Direct access to .{node.attr} (dependency injection violation)",
                                recommendation=f"Use constructor injection or parameter passing for {node.attr}",
                                code_snippet=snippet
                            ))
            
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {py_file}: {str(e)}")
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_solid_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect SOLID principle violations
        
        Currently focuses on:
        - SRP: Large classes (>500 LOC) → likely doing too much
        
        Future enhancements:
        - OCP: Hardcoded conditionals that should be polymorphic
        - LSP: Incorrect inheritance patterns
        - ISP: Fat interfaces
        - DIP: High-level modules depending on low-level details
        """
        findings = []
        
        # Note: Large classes are handled by _detect_large_classes
        # This detector is reserved for future SOLID checks
        
        return findings
    
    def _detect_di_violations_runtime(self, module_path: Path) -> List[Finding]:
        """
        Detect DI violations from runtime error logs (NEW - Phase 2)
        
        Uses log intelligence to find:
        - AttributeError: NoneType has no attribute 'connection'
        - AttributeError: NoneType has no attribute 'service'
        - AttributeError: NoneType has no attribute 'db_path'
        
        These indicate hardcoded dependencies that fail at runtime.
        
        Returns:
            List of findings from runtime log patterns
        """
        findings = []
        
        # Check if log intelligence available
        if not self.log_adapter or not self.log_adapter.is_available():
            return findings
        
        try:
            # Get error patterns from logs (last 7 days)
            error_patterns = self.log_adapter.detect_error_patterns(hours=168)
            
            # Filter for DI violation patterns
            for pattern in error_patterns:
                pattern_text = pattern.get('pattern', '')
                
                # Check if it's a DI violation (AttributeError on connection/service/db_path)
                if 'AttributeError' in pattern_text:
                    if any(attr in pattern_text.lower() for attr in ['connection', 'service', 'db_path']):
                        # Extract location info
                        locations = pattern.get('locations', [])
                        count = pattern.get('count', 0)
                        severity_str = pattern.get('severity', 'HIGH')
                        
                        # Determine if this affects current module
                        module_name = module_path.name
                        relevant_locations = [
                            loc for loc in locations
                            if module_name.lower() in loc.lower()
                        ]
                        
                        if relevant_locations:
                            # Create finding for each location
                            for location in relevant_locations[:3]:  # Max 3 per pattern
                                # Parse location (format: "file.py:line")
                                try:
                                    file_part, line_part = location.rsplit(':', 1)
                                    line_num = int(line_part)
                                    file_path = module_path / file_part
                                except (ValueError, IndexError):
                                    file_path = module_path
                                    line_num = None
                                
                                findings.append(Finding(
                                    category="DI Violation (Runtime)",
                                    severity=Severity.CRITICAL,  # Runtime failures are critical
                                    file_path=file_path,
                                    line_number=line_num,
                                    description=f"Runtime DI violation detected in logs: {pattern_text[:80]}",
                                    recommendation=(
                                        f"This error occurred {count} times in production. "
                                        "Refactor to use dependency injection instead of hardcoded access. "
                                        "See static DI findings for specific code locations."
                                    ),
                                    code_snippet=f"Pattern: {pattern_text[:60]}..."
                                ))
        
        except Exception as e:
            self.logger.warning(f"Runtime DI detection failed: {str(e)}")
        
        return findings
    
    def _detect_large_classes(self, module_path: Path) -> List[Finding]:
        """
        Detect large classes (>500 LOC)
        
        Large classes often violate Single Responsibility Principle (SRP).
        They should be refactored into smaller, focused classes.
        """
        findings = []
        LARGE_CLASS_THRESHOLD = 500  # Lines of code
        
        for py_file in module_path.rglob('*.py'):
            # Skip files in tests/ directories (but not files with 'test' in name elsewhere)
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                
                # Analyze class sizes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Calculate class LOC (end line - start line)
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            class_loc = node.end_lineno - node.lineno + 1
                            
                            if class_loc > LARGE_CLASS_THRESHOLD:
                                findings.append(Finding(
                                    category="Large Class (SRP Violation)",
                                    severity=Severity.MEDIUM,
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    description=f"Class '{node.name}' is {class_loc} lines (>{LARGE_CLASS_THRESHOLD} LOC threshold)",
                                    recommendation=f"Consider refactoring '{node.name}' into smaller, focused classes following SRP"
                                ))
            
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {py_file}: {str(e)}")
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_repository_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect Repository Pattern violations (NEW - v4.6)
        
        Detects violations of Repository Pattern v3.0.0:
        1. Direct import of private implementations (_SqliteRepository, _HanaRepository)
        2. Accessing private repository attributes (._connection, ._cursor)
        3. Using deprecated DataSource pattern (sqlite_data_source, hana_data_source)
        4. Direct database library usage (sqlite3, hdbcli) in business modules
        
        Based on Repository Pattern documentation in:
        docs/knowledge/repository-pattern-modular-architecture.md
        """
        findings = []
        
        # Only check modules/ directory (not core/)
        if 'core' in str(module_path):
            return findings  # Core/ is allowed to use implementations
        
        for py_file in module_path.rglob('*.py'):
            # Skip test files
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # 1. Check for private implementation imports (CRITICAL)
                if '_sqlite_repository' in content or '_hana_repository' in content:
                    for i, line in enumerate(lines, 1):
                        if '_sqlite_repository' in line or '_hana_repository' in line:
                            findings.append(Finding(
                                category="Repository Pattern Violation",
                                severity=Severity.CRITICAL,
                                file_path=py_file,
                                line_number=i,
                                description="Direct import of private repository implementation",
                                recommendation="Use create_repository() factory from core.repositories instead",
                                code_snippet=line.strip()
                            ))
                
                # 2. Check for private attribute access (HIGH)
                tree = ast.parse(content, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute):
                        # Check for ._connection, ._cursor, ._conn
                        if node.attr in ['_connection', '_cursor', '_conn']:
                            line_num = node.lineno
                            snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                            
                            findings.append(Finding(
                                category="Repository Pattern Violation",
                                severity=Severity.HIGH,
                                file_path=py_file,
                                line_number=line_num,
                                description=f"Access to private repository attribute .{node.attr}",
                                recommendation="Use public AbstractRepository interface methods only",
                                code_snippet=snippet
                            ))
                
                # 3. Check for deprecated DataSource usage (MEDIUM)
                if 'sqlite_data_source' in content or 'hana_data_source' in content:
                    for i, line in enumerate(lines, 1):
                        if 'sqlite_data_source' in line or 'hana_data_source' in line:
                            findings.append(Finding(
                                category="Deprecated Pattern",
                                severity=Severity.MEDIUM,
                                file_path=py_file,
                                line_number=i,
                                description="Using deprecated DataSource pattern",
                                recommendation="Migrate to Repository Pattern (use app.sqlite_repository instead)",
                                code_snippet=line.strip()
                            ))
                
                # 4. Check for direct database library usage (MEDIUM)
                if 'import sqlite3' in content or 'import hdbcli' in content:
                    for i, line in enumerate(lines, 1):
                        if 'import sqlite3' in line or 'import hdbcli' in line:
                            findings.append(Finding(
                                category="Repository Pattern Violation",
                                severity=Severity.MEDIUM,
                                file_path=py_file,
                                line_number=i,
                                description="Direct database library import in business module",
                                recommendation="Use AbstractRepository interface from core.repositories",
                                code_snippet=line.strip()
                            ))
                
                # 5. Check for .get_connection() calls (deprecated DataSource method)
                if '.get_connection(' in content:
                    for i, line in enumerate(lines, 1):
                        if '.get_connection(' in line:
                            findings.append(Finding(
                                category="Deprecated Pattern",
                                severity=Severity.MEDIUM,
                                file_path=py_file,
                                line_number=i,
                                description="Using deprecated .get_connection() method",
                                recommendation="Use repository.execute_query() or other AbstractRepository methods",
                                code_snippet=line.strip()
                            ))
            
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {py_file}: {str(e)}")
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_unit_of_work_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect Unit of Work pattern violations (NEW - Phase 1)
        
        Detects violations of Unit of Work pattern from Cosmic Python:
        1. Manual commit/rollback on connections (HIGH)
        2. Multiple repository operations without transaction boundary (MEDIUM)
        3. Missing context manager for transactions (MEDIUM)
        
        Based on Unit of Work pattern documentation in:
        docs/knowledge/cosmic-python-patterns.md
        
        Note: This detector only flags violations. Unit of Work pattern is not yet
        implemented in the codebase (Priority 1 HIGH). These findings guide the
        implementation by showing where atomicity is needed.
        """
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            # Skip test files
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                tree = ast.parse(content, filename=str(py_file))
                
                # 1. Detect manual commit/rollback (HIGH)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Check for .commit() or .rollback() calls
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ['commit', 'rollback']:
                                line_num = node.lineno
                                snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                                
                                # Check if it's on a connection object (not UoW)
                                # Simple heuristic: if line contains 'connection' or 'conn'
                                if 'connection' in snippet.lower() or 'conn' in snippet.lower():
                                    findings.append(Finding(
                                        category="Unit of Work Violation",
                                        severity=Severity.HIGH,
                                        file_path=py_file,
                                        line_number=line_num,
                                        description=f"Manual .{node.func.attr}() on connection object",
                                        recommendation=(
                                            "Use Unit of Work pattern for transaction management. "
                                            "Replace manual commit/rollback with 'with uow: ... uow.commit()'. "
                                            "See docs/knowledge/cosmic-python-patterns.md for examples."
                                        ),
                                        code_snippet=snippet
                                    ))
                
                # 2. Detect multiple repository operations in same function (MEDIUM)
                # This suggests need for transaction boundary (Unit of Work)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Count repository method calls in function
                        repo_calls = []
                        for child in ast.walk(node):
                            if isinstance(child, ast.Attribute):
                                # Common repository methods
                                if child.attr in ['execute_query', 'get_data_products', 
                                                 'create', 'update', 'delete', 'save']:
                                    repo_calls.append(child.lineno)
                        
                        # If 2+ repository calls, might need atomicity
                        if len(repo_calls) >= 2:
                            findings.append(Finding(
                                category="Unit of Work Opportunity",
                                severity=Severity.MEDIUM,
                                file_path=py_file,
                                line_number=node.lineno,
                                description=f"Function '{node.name}' has {len(repo_calls)} repository operations (potential atomicity risk)",
                                recommendation=(
                                    "Consider using Unit of Work pattern to ensure all operations succeed or fail together. "
                                    "Example: with uow: repo1.create() → repo2.update() → uow.commit()"
                                ),
                                code_snippet=f"def {node.name}(...): # {len(repo_calls)} repo operations"
                            ))
            
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {py_file}: {str(e)}")
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_service_layer_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect Service Layer pattern violations (NEW - Phase 1)
        
        Detects violations of Service Layer pattern from Cosmic Python:
        1. Business logic in Flask routes (HIGH)
        2. Direct repository access from controllers (MEDIUM)
        3. Routes with >10 lines (code smell for missing Service Layer)
        
        Based on Service Layer pattern documentation in:
        docs/knowledge/cosmic-python-patterns.md
        
        Service Layer should orchestrate use cases, keeping controllers thin.
        """
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            # Skip test files
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            # Only analyze files that likely contain Flask routes
            if not ('api.py' in py_file.name or 'routes' in py_file.name or '__init__.py' in py_file.name):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                tree = ast.parse(content, filename=str(py_file))
                
                # Find Flask route decorators and analyze their functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function has @app.route or @blueprint.route decorator
                        has_route_decorator = False
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if isinstance(decorator.func, ast.Attribute):
                                    if decorator.func.attr == 'route':
                                        has_route_decorator = True
                                        break
                            elif isinstance(decorator, ast.Attribute):
                                if decorator.attr == 'route':
                                    has_route_decorator = True
                                    break
                        
                        if has_route_decorator:
                            # 1. Check route length (>10 lines suggests missing Service Layer)
                            if hasattr(node, 'end_lineno') and node.end_lineno:
                                route_loc = node.end_lineno - node.lineno + 1
                                
                                if route_loc > 10:
                                    findings.append(Finding(
                                        category="Service Layer Opportunity",
                                        severity=Severity.MEDIUM,
                                        file_path=py_file,
                                        line_number=node.lineno,
                                        description=f"Flask route '{node.name}' is {route_loc} lines (>10 LOC suggests business logic)",
                                        recommendation=(
                                            "Extract business logic to Service Layer. "
                                            "Routes should be thin: parse request → call service → return response. "
                                            "See docs/knowledge/cosmic-python-patterns.md for Service Layer pattern."
                                        ),
                                        code_snippet=f"@route\ndef {node.name}(...): # {route_loc} lines"
                                    ))
                            
                            # 2. Check for repository access in route (MEDIUM)
                            has_repo_access = False
                            for child in ast.walk(node):
                                if isinstance(child, ast.Attribute):
                                    # Check for repository access patterns
                                    if child.attr in ['repository', 'sqlite_repository', 'hana_repository']:
                                        has_repo_access = True
                                        break
                                    # Check for repository methods
                                    if child.attr in ['execute_query', 'get_data_products']:
                                        has_repo_access = True
                                        break
                            
                            if has_repo_access:
                                findings.append(Finding(
                                    category="Service Layer Violation",
                                    severity=Severity.MEDIUM,
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    description=f"Flask route '{node.name}' directly accesses repository",
                                    recommendation=(
                                        "Controllers should call Service Layer, not repositories directly. "
                                        "Create a service class (e.g., KPIService) that takes repository in constructor. "
                                        "Route calls service, service handles orchestration."
                                    ),
                                    code_snippet=f"@route\ndef {node.name}(...): # Direct repo access"
                                ))
                            
                            # 3. Check for business logic keywords (if/for/while)
                            has_business_logic = False
                            for child in ast.walk(node):
                                if isinstance(child, (ast.If, ast.For, ast.While)):
                                    # Ignore simple validation (len==1, single if statement)
                                    has_business_logic = True
                                    break
                            
                            if has_business_logic and route_loc > 10:
                                findings.append(Finding(
                                    category="Service Layer Violation",
                                    severity=Severity.HIGH,
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    description=f"Flask route '{node.name}' contains business logic (if/for/while statements)",
                                    recommendation=(
                                        "Business logic belongs in Service Layer, not controllers. "
                                        "Extract decision logic to a service method. "
                                        "Controllers should be pure orchestration: parse → call service → format response."
                                    ),
                                    code_snippet=f"@route\ndef {node.name}(...): # Contains if/for/while"
                                ))
            
            except SyntaxError as e:
                self.logger.warning(f"Syntax error in {py_file}: {str(e)}")
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_facade_pattern_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect Facade Pattern violations (NEW - v4.9)
        
        Detects violations of Facade Pattern:
        1. API directly imports repositories (should use facade) - HIGH
        2. Facade missing (no facade/ directory) - MEDIUM
        3. Facade not using factory pattern - MEDIUM
        4. API has business logic (should delegate to facade) - HIGH
        
        Facade Pattern provides simplified interface to complex subsystems.
        In our architecture: API → Facade → Repositories
        """
        findings = []
        
        # Check if facade/ directory exists
        facade_dir = module_path / "facade"
        if not facade_dir.exists():
            # Only flag if backend/ exists (indicates backend module)
            backend_dir = module_path / "backend"
            if backend_dir.exists():
                findings.append(Finding(
                    category="Facade Pattern Violation",
                    severity=Severity.MEDIUM,
                    file_path=module_path,
                    line_number=None,
                    description="Module has backend/ but missing facade/ directory",
                    recommendation=(
                        "Create facade layer to orchestrate business logic. "
                        "Facade should use repositories via factory pattern. "
                        "API endpoints should be thin: parse request → call facade → return response."
                    ),
                    code_snippet="mkdir facade/"
                ))
            return findings  # No facade to check
        
        # Check API layer for violations
        backend_dir = module_path / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob('*.py'):
                # Focus on api.py files
                if 'api.py' not in py_file.name:
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    
                    # 1. Check for direct repository imports in API (HIGH)
                    repo_import_patterns = [
                        'from modules.',
                        'Repository',
                        'import.*repository'
                    ]
                    
                    has_repo_import = False
                    for i, line in enumerate(lines, 1):
                        # Skip facade imports (those are good!)
                        if 'facade' in line.lower():
                            continue
                        
                        # Check for repository imports
                        if any(pattern in line for pattern in repo_import_patterns):
                            if 'Repository' in line and 'from' in line:
                                has_repo_import = True
                                findings.append(Finding(
                                    category="Facade Pattern Violation",
                                    severity=Severity.HIGH,
                                    file_path=py_file,
                                    line_number=i,
                                    description="API directly imports repository (should use facade)",
                                    recommendation=(
                                        "API should import facade, not repositories. "
                                        "Replace repository imports with: from ..facade import [ModuleName]Facade"
                                    ),
                                    code_snippet=line.strip()
                                ))
                    
                    # 2. Check if API has NO facade import (HIGH - if repos exist)
                    has_facade_import = 'Facade' in content or 'facade' in content
                    
                    if has_repo_import and not has_facade_import:
                        findings.append(Finding(
                            category="Facade Pattern Violation",
                            severity=Severity.HIGH,
                            file_path=py_file,
                            line_number=1,
                            description="API uses repositories directly without facade layer",
                            recommendation=(
                                "Introduce facade layer to orchestrate repository operations. "
                                "Facade provides business logic, API remains thin."
                            ),
                            code_snippet="# Missing: from ..facade import [ModuleName]Facade"
                        ))
                    
                    # 3. Check for business logic in routes (>15 LOC = likely has logic)
                    tree = ast.parse(content, filename=str(py_file))
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check if it's a Flask route
                            has_route = any(
                                isinstance(d, ast.Attribute) and d.attr == 'route'
                                for d in node.decorator_list
                            )
                            
                            if has_route and hasattr(node, 'end_lineno'):
                                route_loc = node.end_lineno - node.lineno + 1
                                
                                if route_loc > 15:
                                    findings.append(Finding(
                                        category="Facade Pattern Opportunity",
                                        severity=Severity.MEDIUM,
                                        file_path=py_file,
                                        line_number=node.lineno,
                                        description=f"Route '{node.name}' is {route_loc} lines (>15 LOC suggests business logic)",
                                        recommendation=(
                                            "Extract business logic to facade. "
                                            "Routes should be: parse → facade.method() → format response."
                                        ),
                                        code_snippet=f"@route\ndef {node.name}(...): # {route_loc} lines"
                                    ))
                
                except SyntaxError as e:
                    self.logger.warning(f"Syntax error in {py_file}: {str(e)}")
                except Exception as e:
                    self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        # Check facade implementation itself
        for py_file in facade_dir.rglob('*.py'):
            if '__init__.py' in py_file.name:
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                # Check if facade uses factory pattern (good practice)
                has_factory = 'Factory' in content or 'factory' in content
                has_direct_import = False
                
                for i, line in enumerate(lines, 1):
                    # Check for direct repository instantiation
                    if 'Repository(' in line and '=' in line:
                        # Skip if it's via factory
                        if 'Factory' not in line and 'factory' not in line:
                            has_direct_import = True
                            findings.append(Finding(
                                category="Facade Pattern Violation",
                                severity=Severity.MEDIUM,
                                file_path=py_file,
                                line_number=i,
                                description="Facade directly instantiates repository (should use factory)",
                                recommendation=(
                                    "Use factory pattern for repository creation. "
                                    "Example: factory = DataProductRepositoryFactory(); repo = factory.create('sqlite')"
                                ),
                                code_snippet=line.strip()
                            ))
            
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_backend_structure_violations(self, module_path: Path) -> List[Finding]:
        """
        Detect backend structure violations (NEW - v4.9)
        
        Detects violations of modular backend structure:
        1. Missing __init__.py in Python packages (CRITICAL)
        2. Incorrect directory structure (backend/ without proper subdirs)
        3. Missing module.json backend configuration (HIGH)
        
        Proper structure for backend modules:
        modules/[name]/
        ├── backend/
        │   ├── __init__.py  ← exports blueprint
        │   └── api.py       ← defines Blueprint()
        ├── repositories/
        │   └── __init__.py  ← exports repositories
        ├── facade/
        │   └── __init__.py  ← exports facade
        └── module.json      ← backend config
        """
        findings = []
        
        # Only check if backend/ directory exists
        backend_dir = module_path / "backend"
        if not backend_dir.exists():
            return findings  # Not a backend module
        
        # 1. Check for __init__.py in all Python package directories
        python_dirs = ['backend', 'repositories', 'facade', 'services', 'domain']
        
        for dir_name in python_dirs:
            dir_path = module_path / dir_name
            if dir_path.exists():
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    findings.append(Finding(
                        category="Backend Structure Violation",
                        severity=Severity.CRITICAL,
                        file_path=dir_path,
                        line_number=None,
                        description=f"Missing __init__.py in {dir_name}/ directory",
                        recommendation=(
                            f"Create {dir_name}/__init__.py to make it a proper Python package. "
                            "Should export main classes/functions for clean imports."
                        ),
                        code_snippet=f"# touch {dir_name}/__init__.py"
                    ))
        
        # 2. Check module.json backend configuration
        module_json = module_path / "module.json"
        if module_json.exists():
            try:
                import json
                config = json.loads(module_json.read_text())
                
                # Check if backend config exists
                if 'backend' not in config:
                    findings.append(Finding(
                        category="Backend Structure Violation",
                        severity=Severity.HIGH,
                        file_path=module_json,
                        line_number=None,
                        description="module.json missing 'backend' configuration",
                        recommendation=(
                            "Add backend config:\n"
                            '"backend": {\n'
                            '  "blueprint": "modules.[name].backend:blueprint",\n'
                            '  "mount_path": "/api/[name]"\n'
                            '}'
                        ),
                        code_snippet="# Missing backend config"
                    ))
                else:
                    # Validate backend config structure
                    backend_config = config['backend']
                    required_fields = ['blueprint', 'mount_path']
                    
                    for field in required_fields:
                        if field not in backend_config:
                            findings.append(Finding(
                                category="Backend Structure Violation",
                                severity=Severity.HIGH,
                                file_path=module_json,
                                line_number=None,
                                description=f"Backend config missing '{field}' field",
                                recommendation=f"Add '{field}' to backend configuration",
                                code_snippet=f"# Missing: \"{field}\": \"...\""
                            ))
            
            except json.JSONDecodeError as e:
                findings.append(Finding(
                    category="Backend Structure Violation",
                    severity=Severity.CRITICAL,
                    file_path=module_json,
                    line_number=None,
                    description=f"Invalid JSON in module.json: {str(e)}",
                    recommendation="Fix JSON syntax in module.json",
                    code_snippet=str(e)
                ))
            except Exception as e:
                self.logger.warning(f"Could not validate module.json: {str(e)}")
        
        # 3. Check backend/__init__.py exports blueprint
        backend_init = backend_dir / "__init__.py"
        if backend_init.exists():
            try:
                content = backend_init.read_text()
                
                # Should export 'blueprint'
                if 'blueprint' not in content:
                    findings.append(Finding(
                        category="Backend Structure Violation",
                        severity=Severity.HIGH,
                        file_path=backend_init,
                        line_number=1,
                        description="backend/__init__.py does not export 'blueprint'",
                        recommendation=(
                            "Export blueprint for auto-registration:\n"
                            "from .api import blueprint\n"
                            "__all__ = ['blueprint']"
                        ),
                        code_snippet="# Missing: blueprint export"
                    ))
            
            except Exception as e:
                self.logger.warning(f"Could not analyze {backend_init}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """
        Generate human-readable summary
        
        Args:
            findings: List of findings
            metrics: Analysis metrics
            
        Returns:
            Summary string
        """
        if not findings:
            return f"✅ Architecture analysis complete: No violations found in {metrics['files_analyzed']} files"
        
        return (
            f"⚠️ Architecture analysis complete: "
            f"{metrics['total_violations']} violations found "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM) "
            f"in {metrics['files_analyzed']} files"
        )
