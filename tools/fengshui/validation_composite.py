#!/usr/bin/env python3
"""
Feng Shui Validation Composite - Composite Pattern
===================================================

Hierarchical validation structure for project analysis.

GoF Pattern: Composite
- Uniform interface for single items and collections
- Recursive composition (Project → Module → File → Class)
- Aggregate validation results automatically
"""
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class ValidationIssue:
    """A single validation issue"""
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    message: str
    location: str
    suggestion: str = ""


class ValidationComponent(ABC):
    """
    Abstract component in validation hierarchy (Composite pattern)
    
    Represents any validatable element:
    - ProjectValidation (composite)
    - ModuleValidation (composite)
    - FileValidation (leaf)
    - ClassValidation (leaf)
    """
    
    def __init__(self, name: str):
        self.name = name
        self.issues: List[ValidationIssue] = []
        self.children: List['ValidationComponent'] = []
    
    def add(self, component: 'ValidationComponent'):
        """Add child component (for composites)"""
        self.children.append(component)
    
    def remove(self, component: 'ValidationComponent'):
        """Remove child component"""
        self.children.remove(component)
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate this component
        
        Returns:
            True if validation passed (no CRITICAL/HIGH issues)
        """
        pass
    
    def get_all_issues(self) -> List[ValidationIssue]:
        """
        Get all issues from this component and children (recursive)
        
        Returns:
            Flat list of all issues in hierarchy
        """
        all_issues = list(self.issues)
        for child in self.children:
            all_issues.extend(child.get_all_issues())
        return all_issues
    
    def get_issue_count(self) -> Dict[str, int]:
        """
        Count issues by severity across hierarchy
        
        Returns:
            Dict mapping severity → count
        """
        all_issues = self.get_all_issues()
        return {
            'CRITICAL': sum(1 for i in all_issues if i.severity == 'CRITICAL'),
            'HIGH': sum(1 for i in all_issues if i.severity == 'HIGH'),
            'MEDIUM': sum(1 for i in all_issues if i.severity == 'MEDIUM'),
            'LOW': sum(1 for i in all_issues if i.severity == 'LOW'),
            'TOTAL': len(all_issues)
        }
    
    def print_summary(self, indent: int = 0):
        """
        Print validation summary (recursive)
        
        Args:
            indent: Indentation level for hierarchical display
        """
        prefix = "  " * indent
        counts = self.get_issue_count()
        
        # Print this component (Windows-safe status)
        status = "[PASS]" if counts['CRITICAL'] == 0 and counts['HIGH'] == 0 else "[FAIL]"
        print(f"{prefix}{status} {self.name} ({counts['TOTAL']} issues)")
        
        # Print children
        for child in self.children:
            child.print_summary(indent + 1)


class ProjectValidation(ValidationComponent):
    """
    Root of validation hierarchy (Composite)
    
    Validates entire project structure
    """
    
    def __init__(self, project_path: Path):
        super().__init__(f"Project: {project_path.name}")
        self.project_path = project_path
    
    def validate(self) -> bool:
        """
        Validate project structure and all modules
        
        Returns:
            True if no critical issues
        """
        # Check project structure
        required_dirs = ['modules', 'core', 'app', 'tests', 'docs']
        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                self.issues.append(ValidationIssue(
                    severity='HIGH',
                    message=f"Missing required directory: {dir_name}/",
                    location=str(self.project_path)
                ))
        
        # Validate all children (modules)
        for child in self.children:
            child.validate()
        
        counts = self.get_issue_count()
        return counts['CRITICAL'] == 0 and counts['HIGH'] == 0


class ModuleValidation(ValidationComponent):
    """
    Module validation (Composite)
    
    Validates module structure and all files within
    """
    
    def __init__(self, module_path: Path):
        super().__init__(f"Module: {module_path.name}")
        self.module_path = module_path
    
    def validate(self) -> bool:
        """
        Validate module structure and all files
        
        Returns:
            True if no critical issues
        """
        # Check module.json
        module_json = self.module_path / 'module.json'
        if not module_json.exists():
            self.issues.append(ValidationIssue(
                severity='CRITICAL',
                message="module.json not found",
                location=str(self.module_path),
                suggestion="Create module.json with name, version, description, enabled"
            ))
        
        # Check README
        readme = self.module_path / 'README.md'
        if not readme.exists():
            self.issues.append(ValidationIssue(
                severity='MEDIUM',
                message="README.md not found",
                location=str(self.module_path),
                suggestion="Document module purpose, usage, and integration"
            ))
        
        # Validate all children (files)
        for child in self.children:
            child.validate()
        
        counts = self.get_issue_count()
        return counts['CRITICAL'] == 0


class FileValidation(ValidationComponent):
    """
    File validation (Leaf or Composite)
    
    Validates individual Python file
    Can contain ClassValidation children
    """
    
    def __init__(self, file_path: Path):
        super().__init__(f"File: {file_path.name}")
        self.file_path = file_path
    
    def validate(self) -> bool:
        """
        Validate file structure and code quality
        
        Returns:
            True if no critical issues
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Basic checks
            if len(source.splitlines()) > 1000:
                self.issues.append(ValidationIssue(
                    severity='HIGH',
                    message=f"File too large ({len(source.splitlines())} lines)",
                    location=str(self.file_path),
                    suggestion="Consider splitting into multiple files"
                ))
            
            # Check for print statements (should use logging)
            if 'print(' in source and self.file_path.name not in ['__main__.py', 'setup.py']:
                self.issues.append(ValidationIssue(
                    severity='LOW',
                    message="Uses print() instead of logging",
                    location=str(self.file_path),
                    suggestion="Replace print() with logging.info/debug/error"
                ))
            
            # Validate children (classes) if any
            for child in self.children:
                child.validate()
                
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity='MEDIUM',
                message=f"Error reading file: {str(e)}",
                location=str(self.file_path)
            ))
        
        return len([i for i in self.issues if i.severity in ['CRITICAL', 'HIGH']]) == 0


class ClassValidation(ValidationComponent):
    """
    Class validation (Leaf)
    
    Validates individual class structure
    """
    
    def __init__(self, class_name: str, file_path: Path, line_count: int):
        super().__init__(f"Class: {class_name}")
        self.class_name = class_name
        self.file_path = file_path
        self.line_count = line_count
    
    def validate(self) -> bool:
        """
        Validate class structure
        
        Returns:
            True if no critical issues
        """
        # Check for god class
        if self.line_count > 500:
            self.issues.append(ValidationIssue(
                severity='HIGH',
                message=f"God class detected ({self.line_count} lines)",
                location=f"{self.file_path.name}::{self.class_name}",
                suggestion="Split into smaller, focused classes following Single Responsibility Principle"
            ))
        
        # Warning for large classes
        elif self.line_count > 300:
            self.issues.append(ValidationIssue(
                severity='MEDIUM',
                message=f"Large class ({self.line_count} lines)",
                location=f"{self.file_path.name}::{self.class_name}",
                suggestion="Consider refactoring if class has multiple responsibilities"
            ))
        
        return len([i for i in self.issues if i.severity in ['CRITICAL', 'HIGH']]) == 0


# ============================================================================
# BUILDER FOR COMPOSITE HIERARCHY
# ============================================================================

class ValidationHierarchyBuilder:
    """
    Builds validation hierarchy from project structure
    
    Demonstrates Composite pattern usage:
    - Constructs tree: Project → Modules → Files → Classes
    - Uniform interface for all levels
    - Recursive validation and reporting
    """
    
    def build_project_validation(self, project_path: Path) -> ProjectValidation:
        """
        Build complete validation hierarchy for project
        
        Args:
            project_path: Root project directory
            
        Returns:
            ProjectValidation root with complete hierarchy
        """
        project = ProjectValidation(project_path)
        
        # Add module validations
        modules_dir = project_path / 'modules'
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    module_validation = self.build_module_validation(module_dir)
                    project.add(module_validation)
        
        return project
    
    def build_module_validation(self, module_path: Path) -> ModuleValidation:
        """
        Build validation hierarchy for module
        
        Args:
            module_path: Module directory
            
        Returns:
            ModuleValidation with file hierarchy
        """
        module = ModuleValidation(module_path)
        
        # Add file validations from backend/
        backend_dir = module_path / 'backend'
        if backend_dir.exists():
            for py_file in backend_dir.glob('*.py'):
                file_validation = self.build_file_validation(py_file)
                module.add(file_validation)
        
        return module
    
    def build_file_validation(self, file_path: Path) -> FileValidation:
        """
        Build validation hierarchy for file
        
        Args:
            file_path: Python file path
            
        Returns:
            FileValidation with class hierarchy
        """
        file_val = FileValidation(file_path)
        
        # Parse file and add class validations
        try:
            import ast
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Count lines in class
                    lines = sum(1 for _ in ast.walk(node))
                    class_val = ClassValidation(node.name, file_path, lines)
                    file_val.add(class_val)
        except:
            pass  # Ignore parse errors
        
        return file_val


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_composite_pattern():
    """
    Demonstrate Composite pattern with validation hierarchy
    """
    print("\n" + "="*80)
    print("FENG SHUI COMPOSITE PATTERN DEMONSTRATION")
    print("="*80 + "\n")
    
    # Build validation hierarchy
    builder = ValidationHierarchyBuilder()
    project = builder.build_project_validation(Path.cwd())
    
    # Validate (recursive through entire hierarchy)
    print("Running validation...")
    project.validate()
    
    # Print results (hierarchical)
    print("\nVALIDATION RESULTS:")
    print("-" * 80)
    project.print_summary()
    
    # Print issue summary
    print("\n" + "="*80)
    print("ISSUE SUMMARY")
    print("="*80)
    counts = project.get_issue_count()
    for severity, count in counts.items():
        if count > 0:
            print(f"  {severity}: {count}")
    
    # Detailed issues for CRITICAL and HIGH
    critical_and_high = [
        i for i in project.get_all_issues() 
        if i.severity in ['CRITICAL', 'HIGH']
    ]
    
    if critical_and_high:
        print("\nCRITICAL & HIGH PRIORITY ISSUES:")
        print("-" * 80)
        for issue in critical_and_high:
            print(f"  [{issue.severity}] {issue.message}")
            print(f"    Location: {issue.location}")
            if issue.suggestion:
                print(f"    Suggestion: {issue.suggestion}")
            print()


if __name__ == '__main__':
    demonstrate_composite_pattern()