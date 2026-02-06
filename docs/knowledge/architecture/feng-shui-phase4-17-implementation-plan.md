# Feng Shui Phase 4-17: Multi-Agent System Implementation Plan

**Status**: 📋 READY FOR IMPLEMENTATION  
**Created**: 2026-02-06  
**Estimated Effort**: 12-16 hours  
**Prerequisites**: Phase 4-15 ✅ + Phase 4-16 ✅ (both complete)

---

## 🎯 Objective

Add **specialized architecture agents** for comprehensive, parallel analysis with cross-validation.

**Transforms**:
```
TODAY (Phase 4-16):  Single ReAct agent analyzes all aspects sequentially
PHASE 4-17:          4 specialized agents analyze in parallel (4x faster)
                     - ArchitectAgent: Patterns & design
                     - SecurityAgent: Security best practices  
                     - PerformanceAgent: Performance optimization
                     - DocumentationAgent: Documentation quality
```

**Key Benefits**:
- **4x Faster**: Parallel agent execution
- **Comprehensive**: Multiple expert perspectives
- **Cross-Validated**: Agents validate each other's findings
- **Specialized**: Each agent is expert in their domain

---

## 📦 Deliverables

### Phase 4-17 Components (9 files)

**New Directory Structure**:
```
tools/fengshui/agents/
├── __init__.py                    # Package exports
├── base_agent.py                  # Abstract base class (80-100 LOC)
├── architect_agent.py             # Architecture analysis (200-250 LOC)
├── security_agent.py              # Security auditing (180-220 LOC)
├── performance_agent.py           # Performance profiling (180-220 LOC)
├── documentation_agent.py         # Documentation assessment (150-180 LOC)
└── orchestrator.py                # Agent coordination (250-300 LOC)

tests/unit/tools/fengshui/agents/
├── __init__.py
├── test_architect_agent.py        # Unit tests (120-150 LOC)
├── test_security_agent.py         # Unit tests (100-120 LOC)
├── test_performance_agent.py      # Unit tests (100-120 LOC)
├── test_documentation_agent.py    # Unit tests (80-100 LOC)
└── test_orchestrator.py           # Unit tests (150-180 LOC)

tests/integration/
└── test_multiagent_integration.py # Integration tests (120-150 LOC)

docs/knowledge/architecture/
└── feng-shui-phase4-17-multiagent.md  # Complete guide (400-500 LOC)
```

**Modified Files**:
1. `tools/fengshui/react_agent.py` - Integration with orchestrator
2. `docs/knowledge/INDEX.md` - Add Phase 4-17 reference

---

## 🏗️ Implementation Steps

### Step 1: Base Agent Interface (1-2 hours)

**File**: `tools/fengshui/agents/base_agent.py`

```python
"""
Base Agent Interface for Feng Shui Multi-Agent System

Defines common interface for all specialized agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum

class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Finding:
    """Single issue found by agent"""
    category: str           # e.g., "DI Violation", "SQL Injection", etc.
    severity: Severity
    file_path: Path
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'category': self.category,
            'severity': self.severity.value,
            'file_path': str(self.file_path),
            'line_number': self.line_number,
            'description': self.description,
            'recommendation': self.recommendation,
            'code_snippet': self.code_snippet
        }

@dataclass
class AgentReport:
    """Report from single agent analysis"""
    agent_name: str
    module_path: Path
    execution_time_seconds: float
    findings: List[Finding]
    metrics: Dict[str, float]  # Agent-specific metrics
    summary: str
    
    def get_critical_count(self) -> int:
        """Count CRITICAL findings"""
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
    
    def get_high_count(self) -> int:
        """Count HIGH findings"""
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'agent_name': self.agent_name,
            'module_path': str(self.module_path),
            'execution_time_seconds': self.execution_time_seconds,
            'findings': [f.to_dict() for f in self.findings],
            'metrics': self.metrics,
            'summary': self.summary
        }

class BaseAgent(ABC):
    """
    Abstract base class for specialized Feng Shui agents
    
    Each agent specializes in a specific domain (architecture, security, etc.)
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"fengshui.agents.{name}")
    
    @abstractmethod
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module and generate report
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with findings and metrics
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of what this agent can detect
        
        Returns:
            List of capability descriptions
        """
        pass
    
    def validate_module_path(self, module_path: Path) -> bool:
        """
        Validate module path exists and is analyzable
        
        Returns:
            True if valid, False otherwise
        """
        if not module_path.exists():
            self.logger.error(f"Module path does not exist: {module_path}")
            return False
        
        if not module_path.is_dir():
            self.logger.error(f"Module path is not a directory: {module_path}")
            return False
        
        return True
```

### Step 2: Architect Agent (2-3 hours)

**File**: `tools/fengshui/agents/architect_agent.py`

```python
"""
Architect Agent - Architecture Patterns & Design Analysis

Specializes in:
- GoF pattern violations
- SOLID principle compliance
- DI violations
- Coupling/cohesion metrics
- Architecture pattern adherence
"""

import ast
import logging
from pathlib import Path
from typing import List
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity

class ArchitectAgent(BaseAgent):
    """Specializes in architecture quality analysis"""
    
    def __init__(self):
        super().__init__("architect")
        self.pattern_detectors = {
            'di_violation': self._detect_di_violations,
            'solid_violation': self._detect_solid_violations,
            'coupling': self._analyze_coupling,
            'cohesion': self._analyze_cohesion
        }
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module architecture
        
        Checks:
        - DI violations (.connection, .service, .db_path access)
        - SOLID principles (especially SRP, DIP)
        - Coupling metrics (fan-in/fan-out)
        - Cohesion metrics (LCOM)
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
        
        # Run all detectors
        for detector_name, detector_func in self.pattern_detectors.items():
            try:
                detector_findings = detector_func(module_path)
                findings.extend(detector_findings)
            except Exception as e:
                self.logger.error(f"Detector {detector_name} failed: {str(e)}")
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        metrics = {
            'total_violations': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'files_analyzed': len(list(module_path.rglob('*.py')))
        }
        
        # Generate summary
        summary = self._generate_summary(findings, metrics)
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            "Dependency Injection (DI) violation detection",
            "SOLID principle compliance checking",
            "Coupling analysis (fan-in/fan-out)",
            "Cohesion analysis (LCOM metric)",
            "GoF pattern identification",
            "Architecture pattern adherence"
        ]
    
    def _detect_di_violations(self, module_path: Path) -> List[Finding]:
        """Detect direct dependency access (DI violations)"""
        findings = []
        
        for py_file in module_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content)
                
                # Look for .connection, .service, .db_path access
                for node in ast.walk(tree):
                    if isinstance(node, ast.Attribute):
                        if node.attr in ['connection', 'service', 'db_path']:
                            findings.append(Finding(
                                category="DI Violation",
                                severity=Severity.HIGH,
                                file_path=py_file,
                                line_number=node.lineno,
                                description=f"Direct access to .{node.attr} (dependency injection violation)",
                                recommendation=f"Use constructor injection or parameter passing for {node.attr}"
                            ))
            
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file}: {str(e)}")
        
        return findings
    
    def _detect_solid_violations(self, module_path: Path) -> List[Finding]:
        """Detect SOLID principle violations"""
        findings = []
        
        # TODO: Implement SOLID checks
        # - SRP: Large classes (>500 LOC)
        # - OCP: Hardcoded conditionals
        # - LSP: Incorrect inheritance
        # - ISP: Fat interfaces
        # - DIP: High-level modules depending on low-level
        
        return findings
    
    def _analyze_coupling(self, module_path: Path) -> List[Finding]:
        """Analyze module coupling metrics"""
        findings = []
        
        # TODO: Calculate fan-in/fan-out
        # High coupling = bad (>7 dependencies)
        
        return findings
    
    def _analyze_cohesion(self, module_path: Path) -> List[Finding]:
        """Analyze class cohesion (LCOM)"""
        findings = []
        
        # TODO: Calculate Lack of Cohesion of Methods (LCOM)
        # High LCOM = low cohesion = bad
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"✅ Architecture analysis complete: No violations found in {metrics['files_analyzed']} files"
        
        return (
            f"⚠️ Architecture analysis complete: "
            f"{metrics['total_violations']} violations found "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH) "
            f"in {metrics['files_analyzed']} files"
        )
```

### Step 3: Security Agent (2-3 hours)

**File**: `tools/fengshui/agents/security_agent.py`

```python
"""
Security Agent - Security Best Practices Analysis

Specializes in:
- Hardcoded secrets detection
- SQL injection risks
- Authentication/authorization issues
- Input validation
- Security headers
"""

import re
import logging
from pathlib import Path
from typing import List
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity

class SecurityAgent(BaseAgent):
    """Specializes in security auditing"""
    
    def __init__(self):
        super().__init__("security")
        
        # Patterns for secret detection
        self.secret_patterns = {
            'password': re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            'api_key': re.compile(r'api[_-]?key\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            'token': re.compile(r'token\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            'secret': re.compile(r'secret\s*=\s*["\'][^"\']+["\']', re.IGNORECASE)
        }
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            re.compile(r'f".*SELECT.*{.*}"', re.IGNORECASE),  # f-string SQL
            re.compile(r'".*SELECT.*"\s*\+', re.IGNORECASE),  # String concat SQL
            re.compile(r'\.format\(.*\).*SELECT', re.IGNORECASE)  # .format() SQL
        ]
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Security audit of module
        
        Checks:
        - Hardcoded secrets (passwords, API keys, tokens)
        - SQL injection vulnerabilities
        - Authentication/authorization patterns
        - Input validation
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
        
        # Analyze all Python files
        for py_file in module_path.rglob('*.py'):
            findings.extend(self._scan_for_secrets(py_file))
            findings.extend(self._scan_for_sql_injection(py_file))
        
        execution_time = time.time() - start_time
        
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'files_scanned': len(list(module_path.rglob('*.py')))
        }
        
        summary = self._generate_summary(findings, metrics)
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            "Hardcoded secrets detection (passwords, API keys, tokens)",
            "SQL injection vulnerability scanning",
            "Authentication/authorization pattern analysis",
            "Input validation checking",
            "Security header validation"
        ]
    
    def _scan_for_secrets(self, file_path: Path) -> List[Finding]:
        """Scan file for hardcoded secrets"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    for secret_type, pattern in self.secret_patterns.items():
                        if pattern.search(line):
                            # Skip if it's a placeholder/example
                            if any(placeholder in line.lower() for placeholder in [
                                'your_', 'example', 'placeholder', 'xxx', '****'
                            ]):
                                continue
                            
                            findings.append(Finding(
                                category="Hardcoded Secret",
                                severity=Severity.CRITICAL,
                                file_path=file_path,
                                line_number=line_num,
                                description=f"Potential hardcoded {secret_type} detected",
                                recommendation="Use environment variables or secure credential storage",
                                code_snippet=line.strip()
                            ))
        
        except Exception as e:
            self.logger.warning(f"Could not scan {file_path}: {str(e)}")
        
        return findings
    
    def _scan_for_sql_injection(self, file_path: Path) -> List[Finding]:
        """Scan for SQL injection vulnerabilities"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for pattern in self.sql_injection_patterns:
                    for match in pattern.finditer(content):
                        line_num = content[:match.start()].count('\n') + 1
                        
                        findings.append(Finding(
                            category="SQL Injection Risk",
                            severity=Severity.HIGH,
                            file_path=file_path,
                            line_number=line_num,
                            description="Potential SQL injection vulnerability (string concatenation)",
                            recommendation="Use parameterized queries or ORM methods",
                            code_snippet=lines[line_num - 1].strip()
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not scan {file_path}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate summary"""
        if not findings:
            return f"✅ Security audit complete: No issues found in {metrics['files_scanned']} files"
        
        return (
            f"⚠️ Security audit complete: "
            f"{metrics['total_findings']} issues found "
            f"({metrics['critical_count']} CRITICAL) "
            f"in {metrics['files_scanned']} files"
        )
```

### Step 4: Performance Agent (2-3 hours)

**File**: `tools/fengshui/agents/performance_agent.py`

```python
"""
Performance Agent - Performance Optimization Analysis

Specializes in:
- N+1 query patterns
- Inefficient algorithms (O(n²) loops)
- Memory leaks
- Caching opportunities
"""

import ast
import logging
from pathlib import Path
from typing import List
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity

class PerformanceAgent(BaseAgent):
    """Specializes in performance analysis"""
    
    def __init__(self):
        super().__init__("performance")
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Performance analysis of module
        
        Checks:
        - N+1 query patterns (loops with database calls)
        - Nested loops (O(n²) complexity)
        - Missing indexes
        - Caching opportunities
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
        
        # Analyze Python files
        for py_file in module_path.rglob('*.py'):
            findings.extend(self._detect_n_plus_one(py_file))
            findings.extend(self._detect_nested_loops(py_file))
        
        execution_time = time.time() - start_time
        
        metrics = {
            'total_findings': len(findings),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'files_analyzed': len(list(module_path.rglob('*.py')))
        }
        
        summary = self._generate_summary(findings, metrics)
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            "N+1 query pattern detection",
            "Nested loop (O(n²)) detection",
            "Memory leak identification",
            "Caching opportunity analysis",
            "Database index recommendations"
        ]
    
    def _detect_n_plus_one(self, file_path: Path) -> List[Finding]:
        """Detect N+1 query patterns"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Look for loops with database calls inside
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    # Check if loop body contains database calls
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Attribute):
                                # Common ORM method names
                                if child.func.attr in ['execute', 'query', 'get', 'filter', 'select']:
                                    findings.append(Finding(
                                        category="N+1 Query Pattern",
                                        severity=Severity.HIGH,
                                        file_path=file_path,
                                        line_number=node.lineno,
                                        description="Potential N+1 query pattern (database call in loop)",
                                        recommendation="Use bulk query or join instead of loop queries"
                                    ))
                                    break  # One finding per loop
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _detect_nested_loops(self, file_path: Path) -> List[Finding]:
        """Detect nested loops (O(n²) complexity)"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Look for nested loops
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    # Check for nested loops
                    for child in ast.walk(node):
                        if child != node and isinstance(child, (ast.For, ast.While)):
                            findings.append(Finding(
                                category="Nested Loop",
                                severity=Severity.MEDIUM,
                                file_path=file_path,
                                line_number=node.lineno,
                                description="Nested loop detected (O(n²) complexity)",
                                recommendation="Consider using dictionary/set lookups or list comprehensions"
                            ))
                            break  # One finding per outer loop
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate summary"""
        if not findings:
            return f"✅ Performance analysis complete: No issues found in {metrics['files_analyzed']} files"
        
        return (
            f"⚠️ Performance analysis complete: "
            f"{metrics['total_findings']} issues found "
            f"({metrics['high_count']} HIGH) "
            f"in {metrics['files_analyzed']} files"
        )
```

### Step 5: Documentation Agent (1-2 hours)

**File**: `tools/fengshui/agents/documentation_agent.py`

```python
"""
Documentation Agent - Documentation Quality Analysis

Specializes in:
- API documentation completeness
- Code comment quality
- README clarity
- Architecture diagrams
- Docstring coverage
"""

import ast
import logging
from pathlib import Path
from typing import List
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity

class DocumentationAgent(BaseAgent):
    """Specializes in documentation assessment"""
    
    def __init__(self):
        super().__init__("documentation")
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Documentation assessment
        
        Checks:
        - README.md exists and is comprehensive
        - Public functions have docstrings
        - Complex logic has comments
        - API documentation exists
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
        
        # Check README
        findings.extend(self._check_readme(module_path))
        
        # Check docstrings
        for py_file in module_path.rglob('*.py'):
            findings.extend(self._check_docstrings(py_file))
        
        execution_time = time.time() - start_time
        
        metrics = {
            'total_findings': len(findings),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'files_checked': len(list(module_path.rglob('*.py')))
        }
        
        summary = self._generate_summary(findings, metrics)
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            "README.md completeness checking",
            "Docstring coverage analysis",
            "Code comment quality assessment",
            "API documentation validation",
            "Architecture diagram verification"
        ]
    
    def _check_readme(self, module_path: Path) -> List[Finding]:
        """Check if README exists and is comprehensive"""
        findings = []
        
        readme_path = module_path / "README.md"
        if not readme_path.exists():
            findings.append(Finding(
                category="Missing README",
                severity=Severity.MEDIUM,
                file_path=module_path,
                line_number=None,
                description="Module lacks README.md file",
                recommendation="Create README.md with module purpose, usage, and examples"
            ))
        else:
            # Check README length (should be >100 chars)
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) < 100:
                findings.append(Finding(
                    category="Insufficient README",
                    severity=Severity.LOW,
                    file_path=readme_path,
                    line_number=None,
                    description="README.md is too brief (< 100 characters)",
                    recommendation="Expand README with detailed description, usage examples, and API reference"
                ))
        
        return findings
    
    def _check_docstrings(self, file_path: Path) -> List[Finding]:
        """Check docstring coverage in Python file"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check functions and classes for docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Skip private methods
                    if node.name.startswith('_') and not node.name.startswith('__'):
                        continue
                    
                    # Check for docstring
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        findings.append(Finding(
                            category="Missing Docstring",
                            severity=Severity.LOW,
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Public {node.__class__.__name__.lower()} '{node.name}' lacks docstring",
                            recommendation="Add docstring describing purpose, parameters, and return value"
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate summary"""
        if not findings:
            return f"✅ Documentation assessment complete: No issues found in {metrics['files_checked']} files"
        
        return (
            f"ℹ️ Documentation assessment complete: "
            f"{metrics['total_findings']} recommendations "
            f"({metrics['medium_count']} MEDIUM priority) "
            f"in {metrics['files_checked']} files"
        )
```

### Step 6: Agent Orchestrator (3-4 hours)

**File**: `tools/fengshui/agents/orchestrator.py`

```python
"""
Agent Orchestrator - Coordinate Multiple Specialized Agents

Manages:
- Parallel agent execution
- Report synthesis
- Conflict resolution
- Comprehensive recommendations
"""

import logging
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import time

from .base_agent import AgentReport, Finding, Severity
from .architect_agent import ArchitectAgent
from .security_agent import SecurityAgent
from .performance_agent import PerformanceAgent
from .documentation_agent import DocumentationAgent

@dataclass
class ComprehensiveReport:
    """Combined report from all agents"""
    module_path: Path
    agent_reports: List[AgentReport]
    synthesized_plan: 'SynthesizedPlan'
    execution_time_seconds: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'module_path': str(self.module_path),
            'agent_reports': [r.to_dict() for r in self.agent_reports],
            'synthesized_plan': self.synthesized_plan.to_dict(),
            'execution_time_seconds': self.execution_time_seconds
        }

@dataclass
class SynthesizedPlan:
    """Unified action plan from multiple agents"""
    prioritized_actions: List[Dict]  # Actions sorted by priority
    conflicts: List[Dict]             # Conflicting recommendations
    metrics_summary: Dict             # Aggregated metrics
    overall_health_score: float       # 0-100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'prioritized_actions': self.prioritized_actions,
            'conflicts': self.conflicts,
            'metrics_summary': self.metrics_summary,
            'overall_health_score': self.overall_health_score
        }

class AgentOrchestrator:
    """
    Coordinate multiple specialized agents
    
    Features:
    - Parallel agent execution (4x faster)
    - Report synthesis
    - Conflict resolution
    - Priority reconciliation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = {
            'architect': ArchitectAgent(),
            'security': SecurityAgent(),
            'performance': PerformanceAgent(),
            'documentation': DocumentationAgent()
        }
    
    def analyze_module_comprehensive(
        self,
        module_path: Path,
        parallel: bool = True,
        max_workers: int = 4
    ) -> ComprehensiveReport:
        """
        Run all agents on module
        
        Args:
            module_path: Path to module directory
            parallel: Enable parallel execution (default True)
            max_workers: Max parallel threads (default 4)
            
        Returns:
            ComprehensiveReport combining all agent findings
        """
        start_time = time.time()
        
        self.logger.info(f"Starting comprehensive analysis of {module_path}")
        self.logger.info(f"Parallel execution: {parallel} (max_workers: {max_workers})")
        
        if parallel:
            agent_reports = self._run_agents_parallel(module_path, max_workers)
        else:
            agent_reports = self._run_agents_sequential(module_path)
        
        # Synthesize reports
        synthesized_plan = self.synthesize_reports(agent_reports)
        
        execution_time = time.time() - start_time
        
        self.logger.info(f"Comprehensive analysis complete in {execution_time:.2f}s")
        
        return ComprehensiveReport(
            module_path=module_path,
            agent_reports=agent_reports,
            synthesized_plan=synthesized_plan,
            execution_time_seconds=execution_time
        )
    
    def _run_agents_parallel(
        self,
        module_path: Path,
        max_workers: int
    ) -> List[AgentReport]:
        """Run agents in parallel"""
        reports = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all agents
            future_to_agent = {
                executor.submit(agent.analyze_module, module_path): agent_name
                for agent_name, agent in self.agents.items()
            }
            
            # Collect results
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    report = future.result()
                    reports.append(report)
                    self.logger.info(f"Agent '{agent_name}' completed: {len(report.findings)} findings")
                except Exception as e:
                    self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
        
        return reports
    
    def _run_agents_sequential(self, module_path: Path) -> List[AgentReport]:
        """Run agents sequentially (fallback)"""
        reports = []
        
        for agent_name, agent in self.agents.items():
            try:
                self.logger.info(f"Running agent: {agent_name}")
                report = agent.analyze_module(module_path)
                reports.append(report)
                self.logger.info(f"Agent '{agent_name}' completed: {len(report.findings)} findings")
            except Exception as e:
                self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
        
        return reports
    
    def synthesize_reports(
        self,
        reports: List[AgentReport]
    ) -> SynthesizedPlan:
        """
        Combine agent reports into unified action plan
        
        Handles:
        - Priority reconciliation (Critical → High → Medium → Low)
        - Conflict detection (agents disagreeing)
        - Metrics aggregation
        - Overall health score calculation
        """
        all_findings = []
        for report in reports:
            all_findings.extend(report.findings)
        
        # Sort findings by severity
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
        all_findings.sort(key=lambda f: severity_order.index(f.severity))
        
        # Create prioritized actions
        prioritized_actions = []
        for finding in all_findings:
            prioritized_actions.append({
                'agent': next(r.agent_name for r in reports if finding in r.findings),
                'category': finding.category,
                'severity': finding.severity.value,
                'file': str(finding.file_path),
                'line': finding.line_number,
                'description': finding.description,
                'recommendation': finding.recommendation
            })
        
        # Detect conflicts (same file/line, different recommendations)
        conflicts = self._detect_conflicts(all_findings)
        
        # Aggregate metrics
        metrics_summary = {
            'total_findings': len(all_findings),
            'by_severity': {
                severity.value: sum(1 for f in all_findings if f.severity == severity)
                for severity in Severity
            },
            'by_agent': {
                report.agent_name: len(report.findings)
                for report in reports
            },
            'total_execution_time': sum(r.execution_time_seconds for r in reports)
        }
        
        # Calculate overall health score (0-100)
        health_score = self._calculate_health_score(all_findings)
        
        return SynthesizedPlan(
            prioritized_actions=prioritized_actions,
            conflicts=conflicts,
            metrics_summary=metrics_summary,
            overall_health_score=health_score
        )
    
    def _detect_conflicts(self, findings: List[Finding]) -> List[Dict]:
        """Detect conflicting recommendations"""
        conflicts = []
        
        # Group findings by file + line
        by_location = {}
        for finding in findings:
            key = (str(finding.file_path), finding.line_number)
            if key not in by_location:
                by_location[key] = []
            by_location[key].append(finding)
        
        # Find locations with multiple findings
        for location, location_findings in by_location.items():
            if len(location_findings) > 1:
                # Check if recommendations differ
                recommendations = set(f.recommendation for f in location_findings)
                if len(recommendations) > 1:
                    conflicts.append({
                        'file': location[0],
                        'line': location[1],
                        'findings': [
                            {
                                'category': f.category,
                                'recommendation': f.recommendation
                            }
                            for f in location_findings
                        ]
                    })
        
        return conflicts
    
    def _calculate_health_score(self, findings: List[Finding]) -> float:
        """
        Calculate overall health score (0-100)
        
        Formula:
        - Start at 100
        - Deduct points per finding (weighted by severity)
        - CRITICAL: -10 points
        - HIGH: -5 points
        - MEDIUM: -2 points
        - LOW: -1 point
        - INFO: -0.5 points
        """
        score = 100.0
        
        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 5,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
            Severity.INFO: 0.5
        }
        
        for finding in findings:
            score -= severity_weights.get(finding.severity, 0)
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def visualize_report(self, report: ComprehensiveReport) -> str:
        """
        Generate ASCII visualization of comprehensive report
        
        Example output:
        ```
        Comprehensive Module Analysis
        ====================================================
        Module: knowledge_graph
        Execution Time: 12.3s (4 agents in parallel)
        
        Overall Health Score: 78/100 (GOOD)
        
        Findings by Agent:
        - [Architect]     12 findings (2 CRITICAL, 5 HIGH)
        - [Security]      3 findings (1 CRITICAL, 2 HIGH)
        - [Performance]   5 findings (0 CRITICAL, 3 HIGH)
        - [Documentation] 8 findings (0 CRITICAL, 0 HIGH)
        
        Top Priority Actions:
        1. [CRITICAL] Fix DI violation in api.py:25
        2. [CRITICAL] Remove hardcoded password in config.py:12
        3. [HIGH] Fix SQL injection risk in service.py:45
        ...
        
        Conflicts Detected: 2
        - config.py:30: Architect vs Security recommendations differ
        - utils.py:100: Performance vs Documentation conflict
        ====================================================
        ```
        """
        lines = []
        
        lines.append("\nComprehensive Module Analysis")
        lines.append("=" * 60)
        lines.append(f"Module: {report.module_path.name}")
        lines.append(f"Execution Time: {report.execution_time_seconds:.1f}s ({len(report.agent_reports)} agents in parallel)")
        lines.append("")
        
        # Health score
        score = report.synthesized_plan.overall_health_score
        score_label = "EXCELLENT" if score >= 90 else "GOOD" if score >= 70 else "NEEDS IMPROVEMENT" if score >= 50 else "CRITICAL"
        lines.append(f"Overall Health Score: {score:.0f}/100 ({score_label})")
        lines.append("")
        
        # Findings by agent
        lines.append("Findings by Agent:")
        for agent_report in report.agent_reports:
            critical = sum(1 for f in agent_report.findings if f.severity == Severity.CRITICAL)
            high = sum(1 for f in agent_report.findings if f.severity == Severity.HIGH)
            lines.append(f"- [{agent_report.agent_name.title():13}] {len(agent_report.findings):2d} findings ({critical} CRITICAL, {high} HIGH)")
        lines.append("")
        
        # Top priority actions
        lines.append("Top Priority Actions:")
        for i, action in enumerate(report.synthesized_plan.prioritized_actions[:10], 1):
            lines.append(f"{i:2d}. [{action['severity'].upper():8}] {action['description'][:60]}")
            if len(action['description']) > 60:
                lines.append(f"              {action['description'][60:]}")
        lines.append("")
        
        # Conflicts
        if report.synthesized_plan.conflicts:
            lines.append(f"Conflicts Detected: {len(report.synthesized_plan.conflicts)}")
            for conflict in report.synthesized_plan.conflicts:
                lines.append(f"- {conflict['file']}:{conflict['line']}: {len(conflict['findings'])} agents have different recommendations")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
```

### Step 7: Integration with ReAct Agent (30 min)

**File**: `tools/fengshui/react_agent.py` (modify existing)

```python
# Add at top of file
from .agents.orchestrator import AgentOrchestrator

class FengShuiReActAgent:
    """Autonomous reasoning agent"""
    
    def __init__(self, automation_engine=None):
        # ... existing init ...
        self.orchestrator = AgentOrchestrator()  # ADD THIS
    
    def run_autonomous_session_with_multiagent(
        self,
        goal: str,
        module_path: Path,
        max_iterations: int = 10,
        use_multiagent: bool = True
    ) -> SessionReport:
        """
        Run autonomous session with multi-agent analysis
        
        NEW: Uses multiple specialized agents for comprehensive analysis
        """
        if use_multiagent:
            # Run multi-agent comprehensive analysis
            comprehensive_report = self.orchestrator.analyze_module_comprehensive(
                module_path,
                parallel=True
            )
            
            # Use synthesized plan to guide improvements
            prioritized_actions = comprehensive_report.synthesized_plan.prioritized_actions
            
            # Execute improvements via automation engine
            # ... implement action execution ...
        else:
            # Fall back to single ReAct agent (existing behavior)
            return self.run_autonomous_session(goal, max_iterations)
```

### Step 8: Unit Tests (4-5 hours)

**Create test files** (see deliverables list above)

Each agent needs:
- Test initialization
- Test analyze_module with mock data
- Test specific detectors
- Test error handling
- Test report generation

**Orchestrator tests need**:
- Test parallel execution
- Test sequential execution
- Test report synthesis
- Test conflict detection
- Test health score calculation

### Step 9: Integration Tests (1-2 hours)

**File**: `tests/integration/test_multiagent_integration.py`

```python
"""
Integration tests for Multi-Agent System
"""

import pytest
from pathlib import Path
from tools.fengshui.agents.orchestrator import AgentOrchestrator

@pytest.mark.integration
def test_multiagent_comprehensive_analysis():
    """Test full multi-agent analysis on real module"""
    # ARRANGE
    orchestrator = AgentOrchestrator()
    module_path = Path("modules/knowledge_graph")
    
    # ACT
    report = orchestrator.analyze_module_comprehensive(
        module_path,
        parallel=True
    )
    
    # ASSERT
    assert len(report.agent_reports) == 4  # All 4 agents ran
    assert report.execution_time_seconds > 0
    assert report.synthesized_plan.overall_health_score >= 0
    assert report.synthesized_plan.overall_health_score <= 100

@pytest.mark.integration
def test_parallel_faster_than_sequential():
    """Test parallel execution is faster"""
    # ARRANGE
    orchestrator = AgentOrchestrator()
    module_path = Path("modules/knowledge_graph")
    
    # ACT - Sequential
    import time
    start = time.time()
    report_seq = orchestrator.analyze_module_comprehensive(module_path, parallel=False)
    time_seq = time.time() - start
    
    # ACT - Parallel
    start = time.time()
    report_par = orchestrator.analyze_module_comprehensive(module_path, parallel=True)
    time_par = time.time() - start
    
    # ASSERT
    speedup = time_seq / time_par
    print(f"Speedup: {speedup:.2f}x")
    assert speedup > 1.5  # At least 1.5x faster (conservative, should be ~4x)
```

### Step 10: Documentation (1-2 hours)

**File**: `docs/knowledge/architecture/feng-shui-phase4-17-multiagent.md`

Structure:
```markdown
# Feng Shui Phase 4-17: Multi-Agent System

## Overview
- What is Multi-Agent Pattern?
- Why specialized agents?
- Parallel execution benefits

## Architecture
- BaseAgent interface
- 4 Specialized agents (Architect, Security, Performance, Documentation)
- AgentOrchestrator coordination

## Usage Examples
```python
# Example 1: Comprehensive analysis
# Example 2: Parallel vs sequential
# Example 3: Report synthesis
```

## Agent Capabilities
### ArchitectAgent
- DI violations
- SOLID principles
- Coupling/cohesion

### SecurityAgent
- Hardcoded secrets
- SQL injection
- Auth/authz

### PerformanceAgent
- N+1 queries
- Nested loops
- Caching

### DocumentationAgent
- README completeness
- Docstring coverage
- Comment quality

## Integration with ReAct Agent
- Combined autonomous + multi-agent
- Prioritized action execution

## Troubleshooting
- Parallel execution issues
- Agent conflicts
- Performance tuning
```

---

## 🧪 Testing Strategy

### Unit Tests (Expected: 25-30 tests)
- BaseAgent: 3-4 tests
- ArchitectAgent: 6-7 tests
- SecurityAgent: 5-6 tests
- PerformanceAgent: 5-6 tests
- DocumentationAgent: 4-5 tests
- Orchestrator: 8-10 tests

### Integration Tests (Expected: 2-3 tests)
- Comprehensive analysis end-to-end
- Parallel speedup validation
- Real module analysis

### Success Criteria
- ✅ All unit tests passing (25+/25+)
- ✅ All integration tests passing (2+/2+)
- ✅ Parallel execution ≥ 2x faster (target: 4x)
- ✅ 4 agents operational
- ✅ Report synthesis working

---

## 📊 Validation Checklist

**Test 1: Agent Capabilities**
```bash
python -m tools.fengshui.agents.orchestrator --list-capabilities
# Expected: Lists capabilities of all 4 agents
```

**Test 2: Comprehensive Analysis**
```bash
python -m tools.fengshui.agents.orchestrator --module knowledge_graph
# Expected: Reports from all 4 agents with synthesized plan
```

**Test 3: Parallel Speedup**
```bash
python -m tools.fengshui.agents.orchestrator --module knowledge_graph --benchmark
# Expected: Shows sequential vs parallel time (≥2x speedup)
```

**Test 4: Integration with ReAct**
```python
from tools.fengshui.react_agent import FengShuiReActAgent
from pathlib import Path

agent = FengShuiReActAgent()
report = agent.run_autonomous_session_with_multiagent(
    goal="score >= 90",
    module_path=Path("modules/knowledge_graph"),
    use_multiagent=True
)

print(f"Health Score: {report.health_score}")
print(f"Agents Used: {len(report.agent_reports)}")
```

---

## ⏱️ Time Estimates

| Task | Estimated Time | Cumulative |
|------|---------------|------------|
| Step 1: BaseAgent | 1-2 hours | 1-2h |
| Step 2: ArchitectAgent | 2-3 hours | 3-5h |
| Step 3: SecurityAgent | 2-3 hours | 5-8h |
| Step 4: PerformanceAgent | 2-3 hours | 7-11h |
| Step 5: DocumentationAgent | 1-2 hours | 8-13h |
| Step 6: Orchestrator | 3-4 hours | 11-17h |
| Step 7: ReAct integration | 30 min | 11.5-17.5h |
| Step 8: Unit tests | 4-5 hours | 15.5-22.5h |
| Step 9: Integration tests | 1-2 hours | 16.5-24.5h |
| Step 10: Documentation | 1-2 hours | 17.5-26.5h |
| **TOTAL** | **17-26 hours** | - |

**Note**: Original estimate 12-16 hours, revised to 17-26 hours for comprehensive testing.

---

## 🎯 Success Metrics

### Performance Goals
- **Parallel Speedup**: ≥ 2x faster than sequential (target: 4x with 4 workers)
- **Per-Agent Time**: ≤ 30 seconds per module
- **Report Synthesis**: < 5 seconds
- **Overall Analysis**: ≤ 2 minutes for typical module (parallel)

### Quality Goals
- **Test Coverage**: ≥ 80% for new components
- **Agent Accuracy**: ≥ 90% true positive rate (minimal false alarms)
- **Conflict Resolution**: Handles 100% of agent conflicts gracefully
- **Report Completeness**: All 4 agents contribute to final report

---

## 🔄 Backward Compatibility

**CRITICAL**: All existing usage patterns must work

```python
# EXISTING: ReAct agent only (still works)
agent = FengShuiReActAgent()
report = agent.run_autonomous_session(goal="score >= 90")

# EXISTING: With planning (still works)
report = agent.run_autonomous_session_with_planning(
    goal="score >= 90",
    parallel=True
)

# NEW: With multi-agent (opt-in)
report = agent.run_autonomous_session_with_multiagent(
    goal="score >= 90",
    module_path=Path("modules/knowledge_graph"),
    use_multiagent=True
)
```

---

## 📝 Next Steps

### Before Implementation
- [ ] Review this plan
- [ ] Verify Phase 4-15 + 4-16 complete (✅ both done!)
- [ ] Clean git state
- [ ] Create branch: `feature/feng-shui-phase4-17-multiagent`

### During Implementation
- [ ] Follow TDD: Write tests first
- [ ] Implement agents incrementally (one at a time)
- [ ] Test continuously
- [ ] Document as you build
- [ ] Commit after each agent

### After Implementation
- [ ] Run full test suite (25+ tests)
- [ ] Measure parallel speedup (must be ≥ 2x)
- [ ] Update PROJECT_TRACKER.md
- [ ] Tag: `v3.37-feng-shui-phase4-17-multiagent`

---

**Status**: 📋 READY FOR IMPLEMENTATION  
**Created**: 2026-02-06  
**Prerequisites**: Phase 4-15 ✅ + Phase 4-16 ✅ (both complete)  
**Next**: Begin Phase 4-17 implementation when user is ready