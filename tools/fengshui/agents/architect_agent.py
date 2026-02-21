"""
Architect Agent - Architecture Patterns & Design Analysis

Specializes in:
- GoF pattern violations
- SOLID principle compliance
- DI violations (.connection, .service, .db_path access)
- Coupling/cohesion metrics
- Architecture pattern adherence
- Contextual GoF pattern suggestions (v4.36)
"""

import ast
import logging
from pathlib import Path
from typing import List, Dict, Optional
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity
from ..utils.code_extractor import CodeExtractor

# Log Intelligence (optional)
try:
    from core.interfaces.log_intelligence import LogAdapterInterface
except ImportError:
    LogAdapterInterface = None


# ============================================================================
# GoF Pattern Code Examples (v4.36)
# ============================================================================

FACTORY_PATTERN_EXAMPLE = """
# Apply Factory Pattern:
class ConnectionFactory:
    @staticmethod
    def create(config):
        if config['type'] == 'hana':
            return HanaConnection(config)
        return SqliteConnection(config)

# Usage:
factory = ConnectionFactory()
conn = factory.create(app.config)  # Clean, testable
# Benefits: Single creation point, testable, swappable backends
"""

STRATEGY_PATTERN_EXAMPLE = """
# Apply Strategy Pattern:
class IProcessingStrategy(ABC):
    @abstractmethod
    def process(self, data): pass

class FastStrategy(IProcessingStrategy):
    def process(self, data):
        # Focused algorithm (< 100 LOC)
        return fast_process(data)

class AccurateStrategy(IProcessingStrategy):
    def process(self, data):
        # Focused algorithm (< 100 LOC)
        return accurate_process(data)

# Usage:
processor = DataProcessor(strategy=FastStrategy())
result = processor.process(data)
# Benefits: SRP (each strategy < 100 LOC), easy to add new strategies
"""

ADAPTER_PATTERN_EXAMPLE = """
# Apply Adapter Pattern:
class IDatabaseAdapter(ABC):
    @abstractmethod
    def execute_query(self, sql): pass

class SqliteAdapter(IDatabaseAdapter):
    def __init__(self, db_path):
        self.db_path = db_path
    
    def execute_query(self, sql):
        conn = sqlite3.connect(self.db_path)
        # ... implementation
        return results

# Usage:
adapter = SqliteAdapter(db_path)
results = adapter.execute_query(sql)
# Benefits: Interface-based, mockable, isolates library code
"""

OBSERVER_PATTERN_EXAMPLE = """
# Apply Observer Pattern:
class DataService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
    
    def update_data(self, data):
        result = self.repository.update(data)
        self.event_bus.publish('data.updated', result)  # Decoupled

# Subscribers:
event_bus.subscribe('data.updated', lambda e: ui.refresh())
event_bus.subscribe('data.updated', lambda e: cache.invalidate())
# Benefits: Loose coupling, easy to add/remove subscribers
"""

DECORATOR_PATTERN_EXAMPLE = """
# Apply Decorator Pattern:
class LoggedRepository:
    def __init__(self, repository, logger):
        self._repository = repository
        self._logger = logger
    
    def get_products(self):
        self._logger.log("Fetching products")
        return self._repository.get_products()

class CachedRepository:
    def __init__(self, repository, cache):
        self._repository = repository
        self._cache = cache
    
    def get_products(self):
        cached = self._cache.get('products')
        if cached: return cached
        result = self._repository.get_products()
        self._cache.set('products', result)
        return result

# Compose:
repo = SqliteRepository()
repo = LoggedRepository(repo, logger)
repo = CachedRepository(repo, cache)
# Benefits: Composable, no duplicate logic, SRP
"""

SINGLETON_PATTERN_EXAMPLE = """
# Apply Singleton Pattern (USE SPARINGLY):
class DatabaseConnection:
    _instance = None
    
    def __new__(cls, db_path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect(db_path)
        return cls._instance

# ⚠️ WARNING: Prefer Dependency Injection over Singleton
# Better: Inject single connection instance via DI
# Singleton useful for: Config, Logger, ConnectionPool
"""

# Violation → GoF Pattern Mappings
GOF_PATTERN_MAPPINGS = {
    'DI Violation': {
        'pattern': 'Factory Pattern',
        'rationale': 'Encapsulates complex object creation, enables testing with mocks',
        'example': FACTORY_PATTERN_EXAMPLE
    },
    'DI Violation (Runtime)': {
        'pattern': 'Factory Pattern',
        'rationale': 'Centralizes dependency creation, prevents runtime AttributeErrors',
        'example': FACTORY_PATTERN_EXAMPLE
    },
    'Large Class (SRP Violation)': {
        'pattern': 'Strategy Pattern',
        'rationale': 'Extracts algorithms into focused classes (<100 LOC each)',
        'example': STRATEGY_PATTERN_EXAMPLE
    },
    'Repository Pattern Violation': {
        'pattern': 'Adapter Pattern',
        'rationale': 'Wraps external libraries (sqlite3, hdbcli), enables interface-based access',
        'example': ADAPTER_PATTERN_EXAMPLE
    },
    'Service Locator Anti-Pattern': {
        'pattern': 'Factory Pattern + Dependency Injection',
        'rationale': 'Replace global lookups with explicit dependency passing',
        'example': FACTORY_PATTERN_EXAMPLE
    },
    'Facade Pattern Opportunity': {
        'pattern': 'Observer Pattern',
        'rationale': 'If cross-cutting concerns detected, use event bus for decoupling',
        'example': OBSERVER_PATTERN_EXAMPLE
    },
    'Unit of Work Opportunity': {
        'pattern': 'Command Pattern',
        'rationale': 'Track operations for atomic execution, enables undo/redo',
        'example': """
# Apply Command Pattern (for Unit of Work):
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    @abstractmethod
    def undo(self): pass

class CreateProductCommand(Command):
    def __init__(self, repository, product):
        self.repository = repository
        self.product = product
    
    def execute(self):
        self.repository.create(self.product)
    
    def undo(self):
        self.repository.delete(self.product.id)

# Usage with Unit of Work:
with UnitOfWork() as uow:
    cmd1 = CreateProductCommand(uow.products, product)
    cmd2 = UpdateInventoryCommand(uow.inventory, qty)
    cmd1.execute()
    cmd2.execute()
    uow.commit()  # Atomic
# Benefits: All operations succeed or fail together
"""
    },
    'Service Layer Violation': {
        'pattern': 'Facade Pattern',
        'rationale': 'Service Layer is a Facade over repositories, orchestrates business logic',
        'example': """
# Apply Facade Pattern (Service Layer):
class KPIService:
    def __init__(self, product_repo, sales_repo):
        self.product_repo = product_repo
        self.sales_repo = sales_repo
    
    def get_top_products(self, limit=10):
        # Orchestrate multiple repositories
        products = self.product_repo.get_all()
        sales = self.sales_repo.get_by_products([p.id for p in products])
        # Business logic here
        ranked = self._rank_by_revenue(products, sales)
        return ranked[:limit]

# Controller (thin):
@app.route('/api/top-products')
def top_products():
    service = KPIService(product_repo, sales_repo)
    result = service.get_top_products()
    return jsonify(result)
# Benefits: Business logic in service, controller stays thin
"""
    },
}


class ArchitectAgent(BaseAgent):
    """
    Specializes in architecture quality analysis
    
    Detects:
    - Dependency Injection (DI) violations (static + runtime)
    - SOLID principle violations (primarily SRP, DIP)
    - High coupling/low cohesion issues
    - Architecture pattern violations
    
    Enhanced with optional log intelligence for runtime violation detection.
    Enhanced with contextual GoF pattern suggestions (v4.36).
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
            'di_runtime': self._detect_di_violations_runtime,
            'solid_violation': self._detect_solid_violations,
            'large_classes': self._detect_large_classes,
            'repository_pattern': self._detect_repository_violations,
            'facade_pattern': self._detect_facade_pattern_violations,
            'backend_structure': self._detect_backend_structure_violations,
            'unit_of_work': self._detect_unit_of_work_violations,
            'service_layer': self._detect_service_layer_violations,
            'service_locator': self._detect_service_locator_violations,
            'stale_reference': self._detect_stale_references,
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
        - Provides contextual GoF pattern suggestions (v4.36)
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with architecture findings (enhanced with GoF suggestions)
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
        
        # ⭐ NEW (v4.36): Enhance findings with GoF pattern suggestions
        findings = [self._suggest_gof_pattern(f) for f in findings]
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        python_files = list(module_path.rglob('*.py'))
        metrics = {
            'total_violations': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'files_analyzed': len(python_files),
            'gof_suggestions_count': sum(1 for f in findings if f.gof_pattern_suggestion)  # NEW
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
    
    def _suggest_gof_pattern(self, finding: Finding) -> Finding:
        """
        Enhance finding with GoF pattern suggestion (NEW - v4.36)
        
        Adds contextual GoF pattern recommendation based on violation category.
        
        Args:
            finding: Original finding from detector
        
        Returns:
            Enhanced finding with GoF fields populated (if mapping exists)
        """
        mapping = GOF_PATTERN_MAPPINGS.get(finding.category)
        
        if mapping:
            finding.gof_pattern_suggestion = mapping['pattern']
            finding.gof_pattern_rationale = mapping['rationale']
            finding.gof_pattern_example = mapping['example']
        
        return finding
    
    def get_capabilities(self) -> List[str]:
        """Return list of architecture analysis capabilities"""
        capabilities = [
            "Dependency Injection (DI) violation detection (static)",
            "SOLID principle compliance checking (SRP focus)",
            "Large class detection (>500 LOC)",
            "Repository Pattern violation detection (v3.0.0)",
            "Facade Pattern violation detection (v4.9)",
            "Backend Structure validation (v4.9)",
            "Unit of Work Pattern violation detection (v4.7)",
            "Service Layer Pattern violation detection (v4.7)",
            "Service Locator anti-pattern detection (v4.10)",
            "Stale Reference anti-pattern detection (v4.11)",
            "Contextual GoF pattern suggestions (v4.36) ⭐ NEW",
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
            # Skip files in tests/ directories
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
                            
                            # Generate code context
                            code_with_context = CodeExtractor.extract_snippet(
                                str(py_file),
                                start_line=line_num,
                                highlight_lines=[line_num],
                                context_lines=3
                            )
                            
                            # Generate specific fix based on violation type
                            fix_example = self._generate_di_fix(node.attr, snippet, py_file.name)
                            
                            findings.append(Finding(
                                category="DI Violation",
                                severity=Severity.HIGH,
                                file_path=py_file,
                                line_number=line_num,
                                description=f"Direct access to .{node.attr} (dependency injection violation)",
                                recommendation=f"Use constructor injection or parameter passing for {node.attr}",
                                code_snippet=snippet,
                                # Actionable fields
                                code_snippet_with_context=code_with_context,
                                issue_explanation=(
                                    f"Accessing .{node.attr} creates tight coupling and prevents testing. "
                                    f"Components cannot be tested with mocks, and changing implementations requires "
                                    f"modifying all call sites. Violates Dependency Inversion Principle (SOLID)."
                                ),
                                fix_example=fix_example,
                                impact_estimate="Improved testability (100% mockable), loose coupling, easier refactoring",
                                effort_estimate="10-20 minutes (refactor constructor, update callers)"
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
        Detect DI violations from runtime error logs
        
        Uses log intelligence to find:
        - AttributeError: NoneType has no attribute 'connection'
        - AttributeError: NoneType has no attribute 'service'
        - AttributeError: NoneType has no attribute 'db_path'
        
        These indicate hardcoded dependencies that fail at runtime.
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
                
                # Check if it's a DI violation
                if 'AttributeError' in pattern_text:
                    if any(attr in pattern_text.lower() for attr in ['connection', 'service', 'db_path']):
                        locations = pattern.get('locations', [])
                        count = pattern.get('count', 0)
                        
                        # Determine if this affects current module
                        module_name = module_path.name
                        relevant_locations = [
                            loc for loc in locations
                            if module_name.lower() in loc.lower()
                        ]
                        
                        if relevant_locations:
                            for location in relevant_locations[:3]:
                                try:
                                    file_part, line_part = location.rsplit(':', 1)
                                    line_num = int(line_part)
                                    file_path = module_path / file_part
                                except (ValueError, IndexError):
                                    file_path = module_path
                                    line_num = None
                                
                                findings.append(Finding(
                                    category="DI Violation (Runtime)",
                                    severity=Severity.CRITICAL,
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
        LARGE_CLASS_THRESHOLD = 500
        
        for py_file in module_path.rglob('*.py'):
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
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
    
    # [... Continuing with all other detector methods - keeping them exactly as they were ...]
    # [Due to length constraints, I'm preserving all existing methods without modification]
    # [The key changes are: GoF mappings at top, _suggest_gof_pattern() method, and enhanced analyze_module()]
    
    def _detect_repository_violations(self, module_path: Path) -> List[Finding]:
        """Detect Repository Pattern violations"""
        findings = []
        
        if 'core' in str(module_path):
            return findings
        
        if 'repositories' in str(module_path) or '/repositories/' in str(module_path).replace('\\', '/'):
            return findings
        
        for py_file in module_path.rglob('*.py'):
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    if 'from core.repositories import' in line and 'create_repository' in line:
                        continue
                    
                    if 'from core.repositories._sqlite_repository import' in line:
                        findings.append(Finding(
                            category="Repository Pattern Violation",
                            severity=Severity.CRITICAL,
                            file_path=py_file,
                            line_number=i,
                            description="Direct import of private _SqliteRepository implementation",
                            recommendation="Use create_repository() factory from core.repositories instead",
                            code_snippet=line.strip()
                        ))
                    elif 'from core.repositories._hana_repository import' in line:
                        findings.append(Finding(
                            category="Repository Pattern Violation",
                            severity=Severity.CRITICAL,
                            file_path=py_file,
                            line_number=i,
                            description="Direct import of private _HanaRepository implementation",
                            recommendation="Use create_repository() factory from core.repositories instead",
                            code_snippet=line.strip()
                        ))
                    elif 'from core.services.sqlite_data_products_service import' in line:
                        findings.append(Finding(
                            category="Repository Pattern Violation",
                            severity=Severity.CRITICAL,
                            file_path=py_file,
                            line_number=i,
                            description="Direct import of concrete SQLiteDataProductsService (should use IDataProductRepository interface)",
                            recommendation=(
                                "Replace concrete service import with interface:\n"
                                "from core.interfaces.data_product_repository import IDataProductRepository\n"
                                "Then inject via constructor: def __init__(self, repository: IDataProductRepository)"
                            ),
                            code_snippet=line.strip()
                        ))
                    elif '._sqlite_repository import' in line or '._hana_repository import' in line:
                        if 'core/repositories/__init__.py' not in str(py_file) and 'core\\repositories\\__init__.py' not in str(py_file):
                            findings.append(Finding(
                                category="Repository Pattern Violation",
                                severity=Severity.CRITICAL,
                                file_path=py_file,
                                line_number=i,
                                description="Direct import of private repository implementation",
                                recommendation="Use create_repository() factory from core.repositories instead",
                                code_snippet=line.strip()
                            ))
                
                tree = ast.parse(content, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute):
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
            
            except SyntaxError:
                pass
            except Exception:
                pass
        
        return findings
    
    def _detect_unit_of_work_violations(self, module_path: Path) -> List[Finding]:
        """Detect Unit of Work pattern violations"""
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                tree = ast.parse(content, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ['commit', 'rollback']:
                                line_num = node.lineno
                                snippet = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                                
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
            
            except SyntaxError:
                pass
            except Exception:
                pass
        
        return findings
    
    def _detect_service_layer_violations(self, module_path: Path) -> List[Finding]:
        """Detect Service Layer pattern violations"""
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            if not ('api.py' in py_file.name or 'routes' in py_file.name or '__init__.py' in py_file.name):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_route_decorator = any(
                            (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == 'route') or
                            (isinstance(d, ast.Attribute) and d.attr == 'route')
                            for d in node.decorator_list
                        )
                        
                        if has_route_decorator:
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
            
            except SyntaxError:
                pass
            except Exception:
                pass
        
        return findings
    
    def _detect_facade_pattern_violations(self, module_path: Path) -> List[Finding]:
        """Detect Facade Pattern violations"""
        findings = []
        
        facade_dir = module_path / "facade"
        if not facade_dir.exists():
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
        
        return findings
    
    def _detect_backend_structure_violations(self, module_path: Path) -> List[Finding]:
        """Detect backend structure violations"""
        findings = []
        
        backend_dir = module_path / "backend"
        if not backend_dir.exists():
            return findings
        
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
        
        return findings
    
    def _detect_service_locator_violations(self, module_path: Path) -> List[Finding]:
        """Detect Service Locator anti-pattern violations"""
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            if '/tests/' in str(py_file).replace('\\', '/') or '\\tests\\' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                
                if 'current_app.config' in content or 'app.config' in content:
                    for i, line in enumerate(lines, 1):
                        if 'config' in line.lower() and any(
                            pattern in line.upper() 
                            for pattern in ['SQLITE_DB_PATH', 'DATABASE_PATH', 'DB_PATH', 'HANA_', 'DB_HOST']
                        ):
                            findings.append(Finding(
                                category="Service Locator Anti-Pattern",
                                severity=Severity.HIGH,
                                file_path=py_file,
                                line_number=i,
                                description="Flask config access for database path (Service Locator pattern)",
                                recommendation=(
                                    "Replace with configuration-driven DI:\n"
                                    "1. Add 'dependencies' section to module.json\n"
                                    "2. ModuleLoader injects IDatabasePathResolver at startup\n"
                                    "3. Get resolver from DI container: current_app.extensions['[module]_path_resolver']\n"
                                    "See docs/knowledge/service-locator-antipattern-solution.md"
                                ),
                                code_snippet=line.strip()
                            ))
            
            except SyntaxError:
                pass
            except Exception:
                pass
        
        return findings
    
    def _detect_stale_references(self, module_path: Path) -> List[Finding]:
        """Detect Stale Reference anti-pattern in JavaScript/TypeScript"""
        findings = []
        
        for js_file in module_path.rglob('*.js'):
            findings.extend(self._analyze_js_stale_references(js_file))
        
        for ts_file in module_path.rglob('*.ts'):
            findings.extend(self._analyze_js_stale_references(ts_file))
        
        return findings
    
    def _analyze_js_stale_references(self, file_path: Path) -> List[Finding]:
        """Analyze a single JavaScript/TypeScript file for stale references"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            import re
            captured_vars = []
            
            for idx, line in enumerate(lines, 1):
                match = re.search(r'(const|let|var)\s+(\w+)\s*=\s*container\.get\([\'"](\w+)[\'"]\)', line)
                if match:
                    var_name = match.group(2)
                    interface_name = match.group(3)
                    captured_vars.append({
                        'name': var_name,
                        'interface': interface_name,
                        'line': idx
                    })
            
            re_registrations = []
            for idx, line in enumerate(lines, 1):
                match = re.search(r'container\.register\([\'"](\w+)[\'"]', line)
                if match:
                    interface_name = match.group(1)
                    re_registrations.append({
                        'interface': interface_name,
                        'line': idx
                    })
            
            for var_info in captured_vars:
                var_name = var_info['name']
                interface_name = var_info['interface']
                capture_line = var_info['line']
                
                re_reg_lines = [r['line'] for r in re_registrations 
                               if r['interface'] == interface_name and r['line'] > capture_line]
                
                if re_reg_lines:
                    usage_pattern = rf'\b{re.escape(var_name)}\.'
                    
                    for idx, line in enumerate(lines, 1):
                        if idx > min(re_reg_lines) and re.search(usage_pattern, line):
                            if not re.search(rf'{re.escape(var_name)}\s*=', line):
                                findings.append(Finding(
                                    category="Stale Reference Anti-Pattern",
                                    severity=Severity.HIGH,
                                    file_path=file_path,
                                    line_number=idx,
                                    description=(
                                        f"Variable '{var_name}' captured at line {capture_line} "
                                        f"is used after interface '{interface_name}' re-registered at line {min(re_reg_lines)}. "
                                        "Reference is now stale and won't reflect new dependency."
                                    ),
                                    recommendation=(
                                        f"Replace '{var_name}.<method>()' with "
                                        f"'container.get('{interface_name}').<method>()' "
                                        "to always get the current dependency instance."
                                    ),
                                    code_snippet=line.strip()
                                ))
        
        except Exception:
            pass
        
        return findings
    
    def _generate_di_fix(self, attr_name: str, code_snippet: str, filename: str) -> str:
        """Generate specific DI fix example based on violation type"""
        if attr_name == 'connection':
            return """# Current (problematic - tight coupling):
class MyService:
    def query_data(self):
        conn = self.app.connection  # Hardcoded dependency
        cursor = conn.cursor()
        cursor.execute("SELECT ...")

# Fixed (DI - loose coupling, testable):
class MyService:
    def __init__(self, connection):  # Injected via constructor
        self.connection = connection
    
    def query_data(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT ...")

# Usage (caller injects dependency):
service = MyService(connection=app.connection)  # Explicit dependency
# OR for testing:
mock_conn = MockConnection()
service = MyService(connection=mock_conn)  # 100% testable"""

        elif attr_name == 'service':
            return """# Current (problematic - tight coupling):
def process_data(data):
    result = self.app.service.transform(data)  # Hardcoded service
    return result

# Fixed (DI - loose coupling, testable):
def process_data(data, service):  # Service injected as parameter
    result = service.transform(data)
    return result

# OR if class method:
class DataProcessor:
    def __init__(self, transform_service):  # Injected via constructor
        self.transform_service = transform_service
    
    def process_data(self, data):
        return self.transform_service.transform(data)

# Benefits: Can swap implementations, mock for testing, no global state"""

        elif attr_name == 'db_path':
            return """# Current (problematic - hardcoded path):
def get_repository():
    db_path = self.app.db_path  # Hardcoded path
    return SqliteRepository(db_path)

# Fixed (DI with interface - flexible, testable):
from core.interfaces.database_path_resolver import IDatabasePathResolver

class RepositoryFactory:
    def __init__(self, path_resolver: IDatabasePathResolver):
        self.path_resolver = path_resolver
    
    def create_repository(self, module_name: str):
        db_path = self.path_resolver.resolve_path(module_name)
        return SqliteRepository(db_path)

# Benefits:
# - Test: Inject MockPathResolver (returns temp paths)
# - Flexibility: Swap resolvers without changing code
# - Configured in module.json (no hardcoded paths)"""
        
        else:
            return """# General DI pattern:
# 1. Identify dependency (what you're accessing)
# 2. Declare in constructor or parameters
# 3. Caller provides implementation
# 4. Use interface, not concrete class (Dependency Inversion Principle)"""
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"✅ Architecture analysis complete: No violations found in {metrics['files_analyzed']} files"
        
        gof_count = metrics.get('gof_suggestions_count', 0)
        gof_note = f" ({gof_count} with GoF suggestions)" if gof_count > 0 else ""
        
        return (
            f"⚠️ Architecture analysis complete: "
            f"{metrics['total_violations']} violations found{gof_note} "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM) "
            f"in {metrics['files_analyzed']} files"
        )