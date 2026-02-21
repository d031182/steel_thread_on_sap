"""
Preview Mode Validators - Lightweight architecture checks

These validators run BEFORE implementation, checking design specifications
for common Module Federation Standard violations.
"""

from typing import List, Dict, Any
import re
from .engine import PreviewFinding, Severity


class BaseValidator:
    """Base class for preview validators"""
    
    def validate(self, design_spec: Dict[str, Any]) -> List[PreviewFinding]:
        """
        Validate design specification
        
        Args:
            design_spec: Module design specification
            
        Returns:
            List of PreviewFindings
        """
        raise NotImplementedError


class NamingValidator(BaseValidator):
    """
    Validates Module Federation naming conventions
    
    Rules:
    - Module IDs: snake_case (e.g., ai_assistant)
    - Routes: kebab-case (e.g., /ai-assistant)
    - API paths: kebab-case (e.g., /api/ai-assistant)
    - Factory names: PascalCase + 'Module' (e.g., AIAssistantModule)
    """
    
    def validate(self, design_spec: Dict[str, Any]) -> List[PreviewFinding]:
        findings = []
        module_name = design_spec.get('module_name', 'unknown')
        module_id = design_spec.get('module_id', '')
        
        # Check module_id naming
        if module_id:
            if not re.match(r'^[a-z][a-z0-9_]*$', module_id):
                findings.append(PreviewFinding(
                    severity=Severity.HIGH,
                    category='naming_convention',
                    message=f"Module ID '{module_id}' must be snake_case",
                    location=f"{module_name}/module_id",
                    suggestion="Use snake_case for module IDs (e.g., 'ai_assistant', 'data_products_v2')"
                ))
        
        # Check routes naming
        routes = design_spec.get('routes', [])
        for route in routes:
            if not re.match(r'^/[a-z][a-z0-9\-/]*$', route):
                findings.append(PreviewFinding(
                    severity=Severity.MEDIUM,
                    category='naming_convention',
                    message=f"Route '{route}' should use kebab-case",
                    location=f"{module_name}/routes",
                    suggestion="Use kebab-case for routes (e.g., '/ai-assistant', '/data-products')"
                ))
        
        # Check API endpoints naming
        api_endpoints = design_spec.get('api_endpoints', [])
        for endpoint in api_endpoints:
            path = endpoint.get('path', '')
            if path and not re.match(r'^/api/[a-z][a-z0-9\-/]*$', path):
                findings.append(PreviewFinding(
                    severity=Severity.MEDIUM,
                    category='naming_convention',
                    message=f"API path '{path}' should use kebab-case",
                    location=f"{module_name}/api_endpoints",
                    suggestion="Use kebab-case for API paths (e.g., '/api/ai-assistant')"
                ))
        
        # Check factory naming
        factory_name = design_spec.get('factory_name', '')
        if factory_name:
            if not re.match(r'^[A-Z][A-Za-z0-9]*Module$', factory_name):
                findings.append(PreviewFinding(
                    severity=Severity.HIGH,
                    category='naming_convention',
                    message=f"Factory name '{factory_name}' must be PascalCase + 'Module'",
                    location=f"{module_name}/factory_name",
                    suggestion="Use PascalCase + 'Module' suffix (e.g., 'AIAssistantModule')"
                ))
        
        return findings


class StructureValidator(BaseValidator):
    """
    Validates module directory structure
    
    Required structure:
    - module.json (metadata)
    - README.md (documentation)
    - backend/ (Flask Blueprint)
    - frontend/ (Bootstrap)
    - tests/ (API contracts)
    """
    
    def validate(self, design_spec: Dict[str, Any]) -> List[PreviewFinding]:
        findings = []
        module_name = design_spec.get('module_name', 'unknown')
        structure = design_spec.get('structure', {})
        
        # Required files
        required_files = ['module.json', 'README.md']
        for req_file in required_files:
            if req_file not in structure.get('files', []):
                findings.append(PreviewFinding(
                    severity=Severity.CRITICAL,
                    category='missing_required_file',
                    message=f"Missing required file: {req_file}",
                    location=f"{module_name}/",
                    suggestion=f"Create {req_file} as per Module Federation Standard"
                ))
        
        # Required directories
        required_dirs = ['backend', 'frontend', 'tests']
        for req_dir in required_dirs:
            if req_dir not in structure.get('directories', []):
                findings.append(PreviewFinding(
                    severity=Severity.HIGH,
                    category='missing_required_directory',
                    message=f"Missing required directory: {req_dir}/",
                    location=f"{module_name}/",
                    suggestion=f"Create {req_dir}/ directory with proper structure"
                ))
        
        # Backend structure
        backend_files = structure.get('backend_files', [])
        if 'backend' in structure.get('directories', []):
            if 'api.py' not in backend_files:
                findings.append(PreviewFinding(
                    severity=Severity.HIGH,
                    category='missing_backend_file',
                    message="Missing backend/api.py (Flask Blueprint)",
                    location=f"{module_name}/backend/",
                    suggestion="Create backend/api.py with Flask Blueprint"
                ))
        
        # Frontend structure
        frontend_files = structure.get('frontend_files', [])
        if 'frontend' in structure.get('directories', []):
            if 'module.js' not in frontend_files:
                findings.append(PreviewFinding(
                    severity=Severity.HIGH,
                    category='missing_frontend_file',
                    message="Missing frontend/module.js (factory)",
                    location=f"{module_name}/frontend/",
                    suggestion="Create frontend/module.js with factory function"
                ))
        
        return findings


class IsolationValidator(BaseValidator):
    """
    Validates module isolation (no cross-module imports)
    
    Rules:
    - NEVER import from other modules
    - Use core/interfaces/ with Dependency Injection
    - Detected violations: CRITICAL severity
    """
    
    def validate(self, design_spec: Dict[str, Any]) -> List[PreviewFinding]:
        findings = []
        module_name = design_spec.get('module_name', 'unknown')
        dependencies = design_spec.get('dependencies', [])
        
        # Check for cross-module dependencies
        forbidden_patterns = [
            'from modules.',
            'import modules.',
        ]
        
        for dep in dependencies:
            for pattern in forbidden_patterns:
                if pattern in dep:
                    findings.append(PreviewFinding(
                        severity=Severity.CRITICAL,
                        category='module_isolation_violation',
                        message=f"Cross-module import detected: {dep}",
                        location=f"{module_name}/dependencies",
                        suggestion="Use core/interfaces/ with Dependency Injection instead"
                    ))
        
        # Check for core/interfaces usage (recommended)
        has_core_interfaces = any('core.interfaces' in dep for dep in dependencies)
        has_dependencies = len(dependencies) > 0
        
        if has_dependencies and not has_core_interfaces:
            findings.append(PreviewFinding(
                severity=Severity.INFO,
                category='best_practice',
                message="Consider using core/interfaces/ for dependencies",
                location=f"{module_name}/dependencies",
                suggestion="Define interfaces in core/interfaces/ and use DI"
            ))
        
        return findings


class DependencyValidator(BaseValidator):
    """
    Validates dependency management
    
    Rules:
    - External dependencies declared in module.json
    - No circular dependencies
    - Use dependency injection
    """
    
    def validate(self, design_spec: Dict[str, Any]) -> List[PreviewFinding]:
        findings = []
        module_name = design_spec.get('module_name', 'unknown')
        
        # Check if dependencies are declared
        has_module_json = 'module.json' in design_spec.get('structure', {}).get('files', [])
        dependencies = design_spec.get('dependencies', [])
        
        if dependencies and not has_module_json:
            findings.append(PreviewFinding(
                severity=Severity.HIGH,
                category='missing_dependency_declaration',
                message="Dependencies exist but module.json missing",
                location=f"{module_name}/",
                suggestion="Create module.json and declare dependencies"
            ))
        
        return findings


class PatternValidator(BaseValidator):
    """
    Validates architectural patterns
    
    Rules:
    - Repository Pattern for data access
    - Service layer for business logic
    - Adapter pattern for external integrations
    """
    
    def validate(self, design_spec: Dict[str, Any]) -> List[PreviewFinding]:
        findings = []
        module_name = design_spec.get('module_name', 'unknown')
        structure = design_spec.get('structure', {})
        
        # Check for Repository Pattern
        backend_files = structure.get('backend_files', [])
        has_repository = any('repository' in f.lower() for f in backend_files)
        has_data_access = any(
            'database' in str(design_spec).lower() or 
            'query' in str(design_spec).lower()
        )
        
        if has_data_access and not has_repository:
            findings.append(PreviewFinding(
                severity=Severity.MEDIUM,
                category='missing_pattern',
                message="Data access detected but no Repository Pattern",
                location=f"{module_name}/backend/",
                suggestion="Implement Repository Pattern in backend/repositories/"
            ))
        
        # Check for Service layer
        has_service = any('service' in f.lower() for f in backend_files)
        has_business_logic = any(
            endpoint.get('method') == 'POST'
            for endpoint in design_spec.get('api_endpoints', [])
        )
        
        if has_business_logic and not has_service:
            findings.append(PreviewFinding(
                severity=Severity.MEDIUM,
                category='missing_pattern',
                message="Business logic detected but no Service layer",
                location=f"{module_name}/backend/",
                suggestion="Implement Service layer in backend/services/"
            ))
        
        return findings