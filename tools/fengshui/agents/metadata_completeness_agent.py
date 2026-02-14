"""
Metadata Completeness Agent
===========================

Feng Shui agent that detects incomplete metadata propagation from config to API.

Pattern Detected:
- Backend reads module.json (or similar config)
- Backend creates metadata dictionary
- Backend DOESN'T expose all fields that frontend needs
- Frontend breaks due to missing fields

Example from HIGH-16:
```python
# ANTI-PATTERN: Reading but not exposing
config = json.load(f)
metadata = {
    'id': module_id,
    'name': config.get('name'),
    # Missing: 'eager_init' from config!
}

# CORRECT: Expose all relevant fields  
metadata = {
    'id': module_id,
    'name': config.get('name'),
    'eager_init': config.get('eager_init', False),  # ✅ Exposed
}
```

@author P2P Development Team
@version 1.0.0
@date 2026-02-14
"""

import ast
import json
from pathlib import Path
from typing import List, Dict, Set, Any
from tools.fengshui.agents.base_agent import BaseFengShuiAgent, Finding, Severity


class MetadataCompletenessAgent(BaseFengShuiAgent):
    """
    Agent to detect incomplete metadata propagation patterns
    """
    
    def __init__(self):
        super().__init__(
            name="MetadataCompleteness",
            description="Detects config fields not propagated to API responses"
        )
    
    def analyze(self, module_path: Path) -> List[Finding]:
        """
        Analyze module for metadata completeness issues
        
        Args:
            module_path: Path to module directory
            
        Returns:
            List of findings
        """
        findings = []
        
        # Look for services that read module.json
        for py_file in module_path.rglob('*.py'):
            if self._is_excluded(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Find functions that read JSON config
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        findings.extend(self._check_function_metadata_completeness(
                            node, py_file, content
                        ))
                        
            except Exception as e:
                self.logger.debug(f"Error analyzing {py_file}: {e}")
                continue
        
        return findings
    
    def _check_function_metadata_completeness(
        self, 
        func_node: ast.FunctionDef,
        file_path: Path,
        content: str
    ) -> List[Finding]:
        """
        Check if function reads config but doesn't expose all fields
        
        Args:
            func_node: AST function node
            file_path: Path to source file
            content: File content
            
        Returns:
            List of findings
        """
        findings = []
        
        # Check if function reads JSON config
        reads_config = False
        config_var = None
        
        for node in ast.walk(func_node):
            # Look for json.load() or json.loads()
            if isinstance(node, ast.Call):
                if self._is_json_load(node):
                    reads_config = True
                    # Try to find variable name
                    if hasattr(node, 'parent') and isinstance(node.parent, ast.Assign):
                        if node.parent.targets:
                            config_var = node.parent.targets[0].id
        
        if not reads_config:
            return findings
        
        # Function reads config - now check if it creates metadata dict
        for node in ast.walk(func_node):
            if isinstance(node, ast.Dict):
                # Check if this dict accesses config.get()
                config_gets = self._find_config_gets(node, config_var or 'config')
                
                if len(config_gets) > 0:
                    # This is a metadata dict - check if it's incomplete
                    finding = self._check_if_incomplete(
                        node, config_gets, func_node, file_path, content
                    )
                    if finding:
                        findings.append(finding)
        
        return findings
    
    def _is_json_load(self, node: ast.Call) -> bool:
        """Check if node is json.load() or json.loads()"""
        if isinstance(node.func, ast.Attribute):
            if (node.func.attr in ['load', 'loads'] and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'json'):
                return True
        return False
    
    def _find_config_gets(self, dict_node: ast.Dict, config_var: str) -> List[str]:
        """
        Find all config.get('field') calls in dict
        
        Args:
            dict_node: Dictionary AST node
            config_var: Name of config variable
            
        Returns:
            List of field names accessed
        """
        fields = []
        
        for node in ast.walk(dict_node):
            if isinstance(node, ast.Call):
                # Check for config.get('field')
                if (isinstance(node.func, ast.Attribute) and
                    node.func.attr == 'get' and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == config_var):
                    
                    # Get the field name
                    if node.args and isinstance(node.args[0], ast.Constant):
                        fields.append(node.args[0].value)
        
        return fields
    
    def _check_if_incomplete(
        self,
        dict_node: ast.Dict,
        accessed_fields: List[str],
        func_node: ast.FunctionDef,
        file_path: Path,
        content: str
    ) -> Finding | None:
        """
        Check if metadata dict is missing common fields
        
        Args:
            dict_node: Dictionary node
            accessed_fields: Fields accessed from config
            func_node: Parent function node
            file_path: Source file path
            content: File content
            
        Returns:
            Finding if incomplete, None otherwise
        """
        # Common fields that should be propagated
        important_fields = {
            'eager_init': 'Controls module initialization strategy',
            'enabled': 'Controls module availability',
            'order': 'Controls UI ordering',
            'category': 'Groups related modules',
            'features': 'Feature flags for frontend'
        }
        
        # Check if any important fields are missing
        missing_fields = []
        for field, description in important_fields.items():
            if field not in accessed_fields:
                # Check if this field might be in the config
                # (heuristic: if 3+ other fields accessed, likely metadata builder)
                if len(accessed_fields) >= 3:
                    missing_fields.append((field, description))
        
        if not missing_fields:
            return None
        
        # Create finding
        lineno = dict_node.lineno if hasattr(dict_node, 'lineno') else 0
        
        message = (
            f"Function '{func_node.name}' reads config but may not expose all fields\n"
            f"Accessed: {', '.join(accessed_fields)}\n"
            f"Potentially missing: {', '.join(f[0] for f in missing_fields)}"
        )
        
        recommendation = (
            "Add all relevant fields from config to metadata dict:\n"
            + "\n".join(f"  '{field}': config.get('{field}', <default>)  # {desc}"
                       for field, desc in missing_fields)
        )
        
        return Finding(
            agent=self.name,
            severity=Severity.MEDIUM,
            category="Metadata Completeness",
            file=str(file_path.relative_to(Path.cwd())),
            line=lineno,
            message=message,
            recommendation=recommendation,
            context=self._extract_context(content, lineno)
        )
    
    def _is_excluded(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis"""
        excluded = ['test_', '__pycache__', '.pyc', 'venv', 'archive']
        return any(ex in str(file_path) for ex in excluded)
    
    def _extract_context(self, content: str, lineno: int, context_lines: int = 3) -> str:
        """Extract code context around line number"""
        lines = content.split('\n')
        start = max(0, lineno - context_lines - 1)
        end = min(len(lines), lineno + context_lines)
        
        context = []
        for i in range(start, end):
            marker = '>>>' if i == lineno - 1 else '   '
            context.append(f"{marker} {i+1:4d}  {lines[i]}")
        
        return '\n'.join(context)


# Export for Feng Shui orchestrator
__all__ = ['MetadataCompletenessAgent']