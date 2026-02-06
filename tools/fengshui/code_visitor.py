#!/usr/bin/env python3
"""
Feng Shui Code Visitor - Visitor Pattern
=========================================

AST visitor for analyzing Python code structure.

GoF Pattern: Visitor
- Traverse AST once, collect multiple metrics
- Separation of concerns: traversal logic vs analysis logic
- Easy to add new analyses without changing AST structure
"""
import ast
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field


@dataclass
class CodeMetrics:
    """Aggregated metrics from code analysis"""
    file_path: Path
    
    # Complexity metrics
    cyclomatic_complexity: int = 0
    nesting_depth: int = 0
    lines_of_code: int = 0
    
    # Structure metrics
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    # Quality indicators
    has_docstrings: bool = False
    has_type_hints: bool = False
    has_tests: bool = False
    
    # Anti-patterns
    god_class: bool = False  # >500 lines in single class
    long_method: bool = False  # >50 lines in single method
    too_many_params: bool = False  # >5 parameters
    deep_nesting: bool = False  # >4 levels deep
    
    # Dependencies
    external_imports: Set[str] = field(default_factory=set)
    internal_imports: Set[str] = field(default_factory=set)
    
    # Security/Quality
    sql_queries: List[str] = field(default_factory=list)
    potential_vulnerabilities: List[str] = field(default_factory=list)


class CodeVisitor(ABC):
    """
    Abstract visitor for code analysis (Visitor pattern)
    
    Each visitor analyzes one specific aspect of the code.
    Multiple visitors can traverse the same AST without interfering.
    """
    
    def __init__(self):
        self.results: List[Any] = []
    
    @abstractmethod
    def visit(self, node: ast.AST, context: Dict[str, Any]):
        """
        Visit an AST node
        
        Args:
            node: AST node to analyze
            context: Shared context (file path, parent nodes, etc.)
        """
        pass
    
    @abstractmethod
    def get_results(self) -> Any:
        """
        Get analysis results
        
        Returns:
            Results specific to this visitor's analysis
        """
        pass


class ComplexityVisitor(CodeVisitor):
    """
    Analyzes code complexity metrics
    
    Detects:
    - Cyclomatic complexity
    - Nesting depth
    - Method length
    - God classes
    """
    
    def __init__(self):
        super().__init__()
        self.complexity = 0
        self.max_nesting = 0
        self.current_nesting = 0
        self.long_methods = []
        self.god_classes = []
    
    def visit(self, node: ast.AST, context: Dict[str, Any]):
        """Calculate complexity metrics"""
        # Track nesting depth
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            self.current_nesting += 1
            self.max_nesting = max(self.max_nesting, self.current_nesting)
            self.complexity += 1
        
        # Check for long methods
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, 'body'):
                lines = len(node.body)
                if lines > 50:
                    self.long_methods.append(node.name)
        
        # Check for god classes
        if isinstance(node, ast.ClassDef):
            if hasattr(node, 'body'):
                lines = sum(1 for _ in ast.walk(node))
                if lines > 500:
                    self.god_classes.append(node.name)
        
        # Recurse into children
        for child in ast.iter_child_nodes(node):
            self.visit(child, context)
        
        # Untrack nesting when leaving node
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            self.current_nesting -= 1
    
    def get_results(self) -> Dict[str, Any]:
        return {
            'cyclomatic_complexity': self.complexity,
            'max_nesting_depth': self.max_nesting,
            'long_methods': self.long_methods,
            'god_classes': self.god_classes
        }


class DependencyVisitor(CodeVisitor):
    """
    Analyzes module dependencies
    
    Detects:
    - External dependencies
    - Internal module imports
    - Circular import risks
    """
    
    def __init__(self):
        super().__init__()
        self.external_deps: Set[str] = set()
        self.internal_deps: Set[str] = set()
    
    def visit(self, node: ast.AST, context: Dict[str, Any]):
        """Collect import statements"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(('modules.', 'core.', 'app.')):
                    self.internal_deps.add(alias.name)
                else:
                    self.external_deps.add(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.module.startswith(('modules.', 'core.', 'app.')):
                    self.internal_deps.add(node.module)
                else:
                    self.external_deps.add(node.module)
        
        # Recurse
        for child in ast.iter_child_nodes(node):
            self.visit(child, context)
    
    def get_results(self) -> Dict[str, Set[str]]:
        return {
            'external_imports': self.external_deps,
            'internal_imports': self.internal_deps
        }


class SecurityVisitor(CodeVisitor):
    """
    Analyzes security concerns
    
    Detects:
    - SQL injection risks
    - Hardcoded secrets
    - Unsafe file operations
    """
    
    def __init__(self):
        super().__init__()
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.sql_queries: List[str] = []
    
    def visit(self, node: ast.AST, context: Dict[str, Any]):
        """Detect security issues"""
        # Check for f-strings in SQL queries
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr') and node.func.attr == 'execute':
                for arg in node.args:
                    if isinstance(arg, ast.JoinedStr):  # f-string
                        self.vulnerabilities.append({
                            'type': 'SQL_INJECTION',
                            'line': node.lineno,
                            'message': 'f-string in SQL execute()'
                        })
        
        # Check for hardcoded passwords
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if any(keyword in target.id.lower() for keyword in ['password', 'secret', 'key', 'token']):
                        if isinstance(node.value, ast.Constant):
                            self.vulnerabilities.append({
                                'type': 'HARDCODED_SECRET',
                                'line': node.lineno,
                                'variable': target.id
                            })
        
        # Recurse
        for child in ast.iter_child_nodes(node):
            self.visit(child, context)
    
    def get_results(self) -> Dict[str, Any]:
        return {
            'vulnerabilities': self.vulnerabilities,
            'sql_queries': self.sql_queries
        }


class QualityVisitor(CodeVisitor):
    """
    Analyzes code quality indicators
    
    Detects:
    - Missing docstrings
    - Missing type hints
    - Code smells
    """
    
    def __init__(self):
        super().__init__()
        self.functions_without_docstrings: List[str] = []
        self.functions_without_type_hints: List[str] = []
        self.too_many_params: List[str] = []
    
    def visit(self, node: ast.AST, context: Dict[str, Any]):
        """Check code quality"""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check docstring
            if not ast.get_docstring(node):
                self.functions_without_docstrings.append(node.name)
            
            # Check type hints
            if not node.returns:
                self.functions_without_type_hints.append(node.name)
            
            # Check parameter count
            if len(node.args.args) > 5:
                self.too_many_params.append(node.name)
        
        # Recurse
        for child in ast.iter_child_nodes(node):
            self.visit(child, context)
    
    def get_results(self) -> Dict[str, List[str]]:
        return {
            'missing_docstrings': self.functions_without_docstrings,
            'missing_type_hints': self.functions_without_type_hints,
            'too_many_parameters': self.too_many_params
        }


class CodeAnalyzer:
    """
    Coordinates multiple visitors for comprehensive code analysis
    
    This demonstrates the Visitor pattern's power:
    - Single AST traversal
    - Multiple analyses performed simultaneously
    - Each visitor is independent and focused
    """
    
    def __init__(self):
        self.visitors: List[CodeVisitor] = [
            ComplexityVisitor(),
            DependencyVisitor(),
            SecurityVisitor(),
            QualityVisitor()
        ]
    
    def analyze_file(self, file_path: Path) -> CodeMetrics:
        """
        Analyze a Python file with all registered visitors
        
        Args:
            file_path: Path to Python file
            
        Returns:
            CodeMetrics object with all analysis results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse AST
            tree = ast.parse(source, filename=str(file_path))
            
            # Create context
            context = {
                'file_path': file_path,
                'source': source
            }
            
            # Run all visitors (single traversal!)
            for visitor in self.visitors:
                visitor.visit(tree, context)
            
            # Aggregate results
            metrics = CodeMetrics(file_path=file_path)
            metrics.lines_of_code = len(source.splitlines())
            
            # Collect from ComplexityVisitor
            complexity_results = self.visitors[0].get_results()
            metrics.cyclomatic_complexity = complexity_results['cyclomatic_complexity']
            metrics.nesting_depth = complexity_results['max_nesting_depth']
            metrics.long_method = len(complexity_results['long_methods']) > 0
            metrics.god_class = len(complexity_results['god_classes']) > 0
            metrics.deep_nesting = complexity_results['max_nesting_depth'] > 4
            
            # Collect from DependencyVisitor
            dep_results = self.visitors[1].get_results()
            metrics.external_imports = dep_results['external_imports']
            metrics.internal_imports = dep_results['internal_imports']
            
            # Collect from SecurityVisitor
            security_results = self.visitors[2].get_results()
            metrics.potential_vulnerabilities = [
                f"{v['type']} at line {v['line']}" for v in security_results['vulnerabilities']
            ]
            
            # Collect from QualityVisitor
            quality_results = self.visitors[3].get_results()
            metrics.has_docstrings = len(quality_results['missing_docstrings']) == 0
            metrics.has_type_hints = len(quality_results['missing_type_hints']) == 0
            
            return metrics
            
        except Exception as e:
            # Return minimal metrics on error
            return CodeMetrics(
                file_path=file_path,
                potential_vulnerabilities=[f"Analysis error: {str(e)}"]
            )
    
    def analyze_directory(self, directory: Path, recursive: bool = True) -> List[CodeMetrics]:
        """
        Analyze all Python files in directory
        
        Args:
            directory: Directory to analyze
            recursive: Whether to analyze subdirectories
            
        Returns:
            List of CodeMetrics for each file
        """
        results = []
        
        if recursive:
            py_files = directory.rglob('*.py')
        else:
            py_files = directory.glob('*.py')
        
        for py_file in py_files:
            metrics = self.analyze_file(py_file)
            results.append(metrics)
        
        return results


# Example usage
if __name__ == '__main__':
    import sys
    
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Analyze a module
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path('modules/knowledge_graph/backend')
    
    analyzer = CodeAnalyzer()
    
    if target.is_file():
        metrics = analyzer.analyze_file(target)
        print(f"\n{'='*80}")
        print(f"CODE ANALYSIS: {metrics.file_path.name}")
        print(f"{'='*80}")
        print(f"Lines of Code: {metrics.lines_of_code}")
        print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        print(f"Max Nesting Depth: {metrics.nesting_depth}")
        print(f"External Imports: {len(metrics.external_imports)}")
        print(f"Internal Imports: {len(metrics.internal_imports)}")
        
        if metrics.potential_vulnerabilities:
            print(f"\nVulnerabilities:")
            for vuln in metrics.potential_vulnerabilities:
                print(f"  - {vuln}")
    
    else:
        results = analyzer.analyze_directory(target)
        print(f"\n{'='*80}")
        print(f"CODE ANALYSIS: {target}")
        print(f"{'='*80}")
        print(f"Files Analyzed: {len(results)}")
        
        # Summary statistics
        total_loc = sum(m.lines_of_code for m in results)
        avg_complexity = sum(m.cyclomatic_complexity for m in results) / len(results) if results else 0
        files_with_issues = sum(1 for m in results if m.potential_vulnerabilities)
        
        print(f"\nSummary:")
        print(f"  Total Lines: {total_loc}")
        print(f"  Avg Complexity: {avg_complexity:.1f}")
        print(f"  Files with Issues: {files_with_issues}")
        
        # List problematic files
        if files_with_issues:
            print(f"\nFiles Needing Attention:")
            for metrics in results:
                if metrics.god_class:
                    print(f"  - {metrics.file_path.name}: God class detected")
                if metrics.deep_nesting:
                    print(f"  - {metrics.file_path.name}: Deep nesting ({metrics.nesting_depth} levels)")
                if metrics.potential_vulnerabilities:
                    print(f"  - {metrics.file_path.name}: {len(metrics.potential_vulnerabilities)} vulnerabilities")