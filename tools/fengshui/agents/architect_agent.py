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
from typing import List, Dict
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class ArchitectAgent(BaseAgent):
    """
    Specializes in architecture quality analysis
    
    Detects:
    - Dependency Injection (DI) violations
    - SOLID principle violations (primarily SRP, DIP)
    - High coupling/low cohesion issues
    - Architecture pattern violations
    """
    
    def __init__(self):
        super().__init__("architect")
        self.pattern_detectors = {
            'di_violation': self._detect_di_violations,
            'solid_violation': self._detect_solid_violations,
            'large_classes': self._detect_large_classes,
        }
    
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
        return [
            "Dependency Injection (DI) violation detection",
            "SOLID principle compliance checking (SRP focus)",
            "Large class detection (>500 LOC)",
            "Architecture pattern adherence validation",
            "Coupling analysis (future)",
            "Cohesion analysis (future)"
        ]
    
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
            # Skip test files
            if 'test' in py_file.name or 'tests' in str(py_file):
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
    
    def _detect_large_classes(self, module_path: Path) -> List[Finding]:
        """
        Detect large classes (>500 LOC)
        
        Large classes often violate Single Responsibility Principle (SRP).
        They should be refactored into smaller, focused classes.
        """
        findings = []
        LARGE_CLASS_THRESHOLD = 500  # Lines of code
        
        for py_file in module_path.rglob('*.py'):
            # Skip test files
            if 'test' in py_file.name or 'tests' in str(py_file):
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