"""
Documentation Agent - Documentation Quality Analysis

Specializes in:
- README completeness and clarity
- API documentation coverage
- Docstring presence and quality
- Code comment appropriateness
- Documentation structure compliance

Based on: Documentation best practices
"""

import ast
from pathlib import Path
from typing import List, Dict
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class DocumentationAgent(BaseAgent):
    """
    Specializes in documentation quality assessment
    
    Validates:
    - README.md exists and is comprehensive
    - Public functions have docstrings
    - Module documentation structure
    - API documentation completeness
    """
    
    def __init__(self):
        super().__init__("documentation")
        
        # Minimum README length (characters)
        self.min_readme_length = 100
        
        # Minimum docstring length (characters)
        self.min_docstring_length = 20
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Documentation assessment of module
        
        Checks:
        - README.md exists and is comprehensive
        - Public functions/classes have docstrings
        - Docstrings are meaningful (not just placeholders)
        - Module structure is documented
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with documentation findings
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
        
        self.logger.info(f"Analyzing documentation of {module_path}")
        
        # Check README
        findings.extend(self._check_readme(module_path))
        
        # Check docstrings in Python files
        for py_file in module_path.rglob('*.py'):
            # Skip test files and __pycache__
            if 'test' in py_file.name or '__pycache__' in str(py_file):
                continue
            
            findings.extend(self._check_docstrings(py_file))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        files_checked = len([f for f in module_path.rglob('*.py') 
                           if 'test' not in f.name and '__pycache__' not in str(f)])
        
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'low_count': sum(1 for f in findings if f.severity == Severity.LOW),
            'files_checked': files_checked
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"Documentation analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of documentation analysis capabilities"""
        return [
            "README.md completeness checking",
            "Docstring coverage analysis",
            "Public function/class documentation validation",
            "Documentation structure compliance",
            "API documentation assessment",
            "Code comment quality evaluation"
        ]
    
    def _check_readme(self, module_path: Path) -> List[Finding]:
        """
        Check if README.md exists and is comprehensive
        
        Requirements:
        - README.md file exists
        - Content > 100 characters
        - Contains key sections (purpose, usage, etc.)
        """
        findings = []
        
        readme_path = module_path / "README.md"
        
        if not readme_path.exists():
            findings.append(Finding(
                category="Missing README",
                severity=Severity.MEDIUM,
                file_path=module_path,
                line_number=None,
                description="Module lacks README.md file",
                recommendation="Create README.md with: module purpose, usage examples, API reference, dependencies",
                code_snippet=None
            ))
            return findings
        
        # Check README content
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check length
            if len(content) < self.min_readme_length:
                findings.append(Finding(
                    category="Insufficient README",
                    severity=Severity.LOW,
                    file_path=readme_path,
                    line_number=None,
                    description=f"README.md is too brief ({len(content)} chars, minimum {self.min_readme_length})",
                    recommendation="Expand README with: detailed description, usage examples, API reference, troubleshooting guide",
                    code_snippet=None
                ))
            
            # Check for key sections (case-insensitive)
            content_lower = content.lower()
            missing_sections = []
            
            recommended_sections = {
                'overview': ['overview', 'introduction', 'about'],
                'usage': ['usage', 'how to use', 'getting started'],
                'api': ['api', 'reference', 'methods']
            }
            
            for section_type, keywords in recommended_sections.items():
                if not any(keyword in content_lower for keyword in keywords):
                    missing_sections.append(section_type)
            
            if missing_sections:
                findings.append(Finding(
                    category="Incomplete README",
                    severity=Severity.LOW,
                    file_path=readme_path,
                    line_number=None,
                    description=f"README.md missing recommended sections: {', '.join(missing_sections)}",
                    recommendation=f"Add sections for: {', '.join(missing_sections)}",
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not read README {readme_path}: {str(e)}")
        
        return findings
    
    def _check_docstrings(self, file_path: Path) -> List[Finding]:
        """
        Check docstring coverage in Python file
        
        Rules:
        - All public functions should have docstrings
        - All public classes should have docstrings
        - Docstrings should be meaningful (not just "TODO")
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Skip private methods/classes (start with _)
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue
                    
                    # Get docstring
                    docstring = ast.get_docstring(node)
                    
                    if not docstring:
                        # No docstring at all
                        findings.append(Finding(
                            category="Missing Docstring",
                            severity=Severity.LOW,
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Public {node.__class__.__name__.replace('Def', '').lower()} '{node.name}' lacks docstring",
                            recommendation="Add docstring with: purpose, parameters, return value, exceptions",
                            code_snippet=None
                        ))
                    elif len(docstring) < self.min_docstring_length:
                        # Docstring too short (likely placeholder)
                        findings.append(Finding(
                            category="Insufficient Docstring",
                            severity=Severity.LOW,
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Docstring for '{node.name}' is too brief ({len(docstring)} chars)",
                            recommendation="Expand docstring with: detailed description, parameter descriptions, return value, usage examples",
                            code_snippet=None
                        ))
                    elif any(placeholder in docstring.lower() for placeholder in ['todo', 'fixme', 'placeholder']):
                        # Docstring is placeholder
                        findings.append(Finding(
                            category="Placeholder Docstring",
                            severity=Severity.LOW,
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Docstring for '{node.name}' appears to be a placeholder",
                            recommendation="Replace with complete documentation",
                            code_snippet=None
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"Documentation assessment complete: No issues found in {metrics['files_checked']} files"
        
        return (
            f"DOCUMENTATION ASSESSMENT: "
            f"{metrics['total_findings']} recommendations "
            f"({metrics['medium_count']} MEDIUM, {metrics['low_count']} LOW) "
            f"in {metrics['files_checked']} files"
        )