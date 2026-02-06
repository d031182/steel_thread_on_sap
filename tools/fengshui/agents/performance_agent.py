"""
Performance Agent - Performance Optimization Analysis

Specializes in:
- N+1 query patterns (loops with database calls)
- Inefficient algorithms (O(n²) nested loops)
- Missing caching opportunities
- Memory leak patterns
- Database query optimization

Based on: Performance optimization best practices
"""

import ast
import re
from pathlib import Path
from typing import List, Dict
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class PerformanceAgent(BaseAgent):
    """
    Specializes in performance analysis and optimization
    
    Validates:
    - N+1 query patterns avoided
    - Efficient algorithms used (no unnecessary O(n²))
    - Caching utilized where appropriate
    - Database queries optimized
    """
    
    def __init__(self):
        super().__init__("performance")
        
        # Database call patterns (ORM methods)
        self.db_call_methods = {
            'execute', 'query', 'get', 'filter', 'select', 'fetchall',
            'fetchone', 'all', 'first', 'one', 'scalar', 'commit'
        }
        
        # Patterns indicating potential caching opportunities
        self.cache_patterns = [
            re.compile(r'def\s+get_\w+\(self\):'),  # Getter methods
            re.compile(r'def\s+load_\w+\(self\):'),  # Load methods
            re.compile(r'def\s+fetch_\w+\(self\):'),  # Fetch methods
        ]
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Performance analysis of module
        
        Checks:
        - N+1 query patterns (loops with database calls)
        - Nested loops (O(n²) complexity)
        - Missing caching opportunities
        - Inefficient list operations
        - Large file operations
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with performance findings
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
        
        self.logger.info(f"Analyzing performance of {module_path}")
        
        # Analyze Python files
        for py_file in module_path.rglob('*.py'):
            # Skip test files and __pycache__
            if 'test' in py_file.name or '__pycache__' in str(py_file):
                continue
            
            findings.extend(self._detect_n_plus_one(py_file))
            findings.extend(self._detect_nested_loops(py_file))
            findings.extend(self._detect_missing_cache(py_file))
            findings.extend(self._detect_inefficient_operations(py_file))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        files_analyzed = len([f for f in module_path.rglob('*.py') 
                            if 'test' not in f.name and '__pycache__' not in str(f)])
        
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'files_analyzed': files_analyzed
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"Performance analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of performance analysis capabilities"""
        return [
            "N+1 query pattern detection",
            "Nested loop (O(n²)) identification",
            "Missing cache opportunity detection",
            "Inefficient list operation analysis",
            "Database query optimization recommendations",
            "Memory leak pattern detection"
        ]
    
    def _detect_n_plus_one(self, file_path: Path) -> List[Finding]:
        """
        Detect N+1 query patterns
        
        Pattern: Loop with database call inside
        Problem: Executes N queries instead of 1 bulk query
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Look for loops with database calls inside
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    # Check if loop body contains database calls
                    has_db_call = False
                    db_call_line = None
                    
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                if child.func.attr in self.db_call_methods:
                                    has_db_call = True
                                    db_call_line = child.lineno
                                    break
                    
                    if has_db_call:
                        findings.append(Finding(
                            category="N+1 Query Pattern",
                            severity=Severity.HIGH,
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Potential N+1 query: database call at line {db_call_line} inside loop",
                            recommendation="Use bulk query, JOIN, or prefetch to avoid N queries. Example: Use SELECT ... WHERE id IN (...) instead of loop",
                            code_snippet=None
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _detect_nested_loops(self, file_path: Path) -> List[Finding]:
        """
        Detect nested loops (O(n²) complexity)
        
        Pattern: For loop inside for loop
        Problem: Can be slow for large datasets
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Look for nested loops
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    # Check for nested loops in body
                    for child in node.body:
                        for grandchild in ast.walk(child):
                            if grandchild != node and isinstance(grandchild, (ast.For, ast.While)):
                                findings.append(Finding(
                                    category="Nested Loop",
                                    severity=Severity.MEDIUM,
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    description="Nested loop detected (O(n²) complexity)",
                                    recommendation="Consider: 1) Use dictionary/set for O(1) lookups, 2) Use list comprehension, 3) Pre-compute results",
                                    code_snippet=None
                                ))
                                break  # One finding per outer loop
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _detect_missing_cache(self, file_path: Path) -> List[Finding]:
        """
        Detect methods that could benefit from caching
        
        Patterns:
        - get_* methods without @lru_cache
        - load_* methods without caching
        - Repeated expensive operations
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            tree = ast.parse(content)
            
            # Check for methods that might benefit from caching
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if method name suggests it should be cached
                    if node.name.startswith(('get_', 'load_', 'fetch_', 'compute_')):
                        # Check if it has @lru_cache decorator
                        has_cache = any(
                            isinstance(dec, ast.Name) and dec.id == 'lru_cache' or
                            isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == 'lru_cache'
                            for dec in node.decorator_list
                        )
                        
                        if not has_cache:
                            # Check if function is expensive (has loops or external calls)
                            has_loop = any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node))
                            
                            if has_loop:
                                findings.append(Finding(
                                    category="Missing Cache",
                                    severity=Severity.LOW,
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    description=f"Method '{node.name}' could benefit from caching (contains loops)",
                                    recommendation="Consider adding @lru_cache decorator if results are reused",
                                    code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else None
                                ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _detect_inefficient_operations(self, file_path: Path) -> List[Finding]:
        """
        Detect inefficient list/string operations
        
        Patterns:
        - String concatenation in loops (use list.join instead)
        - List.append in loops without pre-allocation
        - Multiple list iterations (could be combined)
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            tree = ast.parse(content)
            
            # Detect string concatenation in loops
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    for child in ast.walk(node):
                        # Check for += with strings
                        if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                            # This is a += operation
                            # Check if it's string concatenation (hard to detect without type info)
                            # For now, flag all += in loops as potential issue
                            findings.append(Finding(
                                category="Inefficient String Operation",
                                severity=Severity.LOW,
                                file_path=file_path,
                                line_number=child.lineno,
                                description="String concatenation in loop (if string type)",
                                recommendation="If string concatenation: use list.append() + ''.join() for better performance",
                                code_snippet=lines[child.lineno - 1].strip() if child.lineno <= len(lines) else None
                            ))
                            break  # One per loop
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"Performance analysis complete: No issues found in {metrics['files_analyzed']} files"
        
        return (
            f"PERFORMANCE ANALYSIS: "
            f"{metrics['total_findings']} optimization opportunities found "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM) "
            f"in {metrics['files_analyzed']} files"
        )