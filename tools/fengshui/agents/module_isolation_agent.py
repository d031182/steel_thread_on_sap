"""
Module Isolation Agent - Enforce Zero Cross-Module Dependencies

This agent ensures modules communicate ONLY through core/interfaces,
never importing directly from each other. This is a CRITICAL architectural
principle for:
- Loose coupling
- Independent deployment
- Easy testing
- No circular dependencies

Industry Standard: Hexagonal Architecture, Clean Architecture, SOLID principles
"""

import re
import time
from pathlib import Path
from typing import List, Dict, Any
from tools.fengshui.agents.base_agent import BaseAgent, AgentReport, Finding, Severity


class ModuleIsolationAgent(BaseAgent):
    """
    Detect and prevent cross-module imports.
    
    Validates that modules depend on core/interfaces (DI),
    not on each other directly.
    """
    
    def __init__(self):
        super().__init__(name="module_isolation")
    
    def analyze(self, project_path: Path) -> List[Dict[str, Any]]:
        """
        Scan all modules for cross-module imports.
        
        Returns:
            List of violations with severity, file, message, fix
        """
        findings = []
        modules_dir = project_path / 'modules'
        
        if not modules_dir.exists():
            return findings
        
        # Get all module directories
        all_modules = [
            m.name for m in modules_dir.iterdir() 
            if m.is_dir() and not m.name.startswith('_')
        ]
        
        # Scan each module
        for module_path in modules_dir.iterdir():
            if not module_path.is_dir() or module_path.name.startswith('_'):
                continue
            
            current_module = module_path.name
            
            # Scan all Python files in module
            for py_file in module_path.rglob('*.py'):
                if '__pycache__' in str(py_file):
                    continue
                
                violations = self._check_file_imports(
                    py_file, 
                    current_module, 
                    all_modules
                )
                findings.extend(violations)
        
        return findings
    
    def _check_file_imports(
        self, 
        py_file: Path, 
        current_module: str, 
        all_modules: List[str]
    ) -> List[Dict[str, Any]]:
        """Check a single file for cross-module imports."""
        violations = []
        
        try:
            content = py_file.read_text(encoding='utf-8')
        except Exception as e:
            return [{
                'category': 'Module Isolation',
                'severity': 'WARNING',
                'file': str(py_file),
                'line': 0,
                'message': f'Could not read file: {e}',
                'fix': 'Ensure file is readable'
            }]
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Pattern 1: from modules.other_module import ...
            match1 = re.search(r'from\s+modules\.(\w+)', line)
            if match1:
                imported_module = match1.group(1)
                if imported_module != current_module and imported_module in all_modules:
                    violations.append({
                        'category': 'Module Isolation',
                        'severity': 'CRITICAL',
                        'file': str(py_file),
                        'line': line_num,
                        'message': (
                            f"Cross-module import: '{current_module}' imports from '{imported_module}'. "
                            f"Modules must communicate via core/interfaces with DI."
                        ),
                        'code': line.strip(),
                        'fix': (
                            f"1. Create interface in core/interfaces/\n"
                            f"2. Have '{imported_module}' implement interface\n"
                            f"3. Inject interface via constructor in '{current_module}'\n"
                            f"4. Wire dependency in server.py (DI container)"
                        )
                    })
            
            # Pattern 2: import modules.other_module
            match2 = re.search(r'import\s+modules\.(\w+)', line)
            if match2:
                imported_module = match2.group(1)
                if imported_module != current_module and imported_module in all_modules:
                    violations.append({
                        'category': 'Module Isolation',
                        'severity': 'CRITICAL',
                        'file': str(py_file),
                        'line': line_num,
                        'message': (
                            f"Cross-module import: '{current_module}' imports '{imported_module}'. "
                            f"Modules must communicate via core/interfaces with DI."
                        ),
                        'code': line.strip(),
                        'fix': (
                            f"1. Create interface in core/interfaces/\n"
                            f"2. Have '{imported_module}' implement interface\n"
                            f"3. Inject interface via constructor in '{current_module}'\n"
                            f"4. Wire dependency in server.py (DI container)"
                        )
                    })
        
        return violations
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze a single module for cross-module imports.
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with findings
        """
        start_time = time.time()
        
        if not self.validate_module_path(module_path):
            return self._create_empty_report(module_path, "Invalid module path")
        
        # Get violations for this module
        all_modules_dir = module_path.parent
        all_modules = [
            m.name for m in all_modules_dir.iterdir() 
            if m.is_dir() and not m.name.startswith('_')
        ]
        
        findings = []
        current_module = module_path.name
        
        # Scan all Python files in this module
        for py_file in module_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            violations = self._check_file_imports(py_file, current_module, all_modules)
            
            # Convert to Finding objects
            for v in violations:
                findings.append(Finding(
                    category=v['category'],
                    severity=Severity.CRITICAL,
                    file_path=Path(v['file']),
                    line_number=v['line'],
                    description=v['message'],
                    recommendation=v['fix'],
                    code_snippet=v.get('code', '')
                ))
        
        execution_time = time.time() - start_time
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics={'violations_count': len(findings)},
            summary=f"Found {len(findings)} cross-module import violation(s)"
        )
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities."""
        return [
            "Detects cross-module imports (modules importing from each other)",
            "Enforces interface-based communication via core/interfaces",
            "Validates Dependency Inversion Principle (SOLID)",
            "Ensures loose coupling between modules",
            "Prevents circular dependencies"
        ]
    
    def get_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Provide architecture recommendations based on violations."""
        if not findings:
            return ["✅ Perfect! All modules properly isolated via interfaces."]
        
        recommendations = [
            "⚠️ Cross-Module Import Violations Detected",
            "",
            "Modules are importing from each other directly. This violates:",
            "- Hexagonal Architecture (Ports & Adapters)",
            "- Clean Architecture (Dependency Inversion)",
            "- SOLID Principles (Dependency Inversion Principle)",
            "",
            "✅ Correct Pattern:",
            "1. Define interface in core/interfaces/",
            "2. Modules implement/depend on interfaces",
            "3. Inject via constructor (Dependency Injection)",
            "4. Wire in server.py (DI container)",
            "",
            "Example:",
            "```python",
            "# core/interfaces/data_source.py",
            "class IDataSource:",
            "    def get_data(self): pass",
            "",
            "# modules/data_products/repositories/sqlite_repository.py",
            "class SqliteRepository(IDataSource):",
            "    def get_data(self):",
            "        return self.db.query('SELECT * FROM products')",
            "",
            "# modules/ai_assistant/services/agent_service.py",
            "class AgentService:",
            "    def __init__(self, data_source: IDataSource):",
            "        self.data_source = data_source  # ✅ Depends on interface",
            "",
            "# server.py (DI Container)",
            "data_source = SqliteRepository()  # Concrete implementation",
            "agent = AgentService(data_source)  # Inject dependency",
            "```",
            "",
            f"Found {len(findings)} violation(s). See details above."
        ]
        
        return recommendations


# Export agent instance
agent = ModuleIsolationAgent()