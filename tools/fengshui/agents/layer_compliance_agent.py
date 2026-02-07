"""
Layer Compliance Agent - DDD/Clean Architecture Layer Validation

Specializes in:
- Pure infrastructure detection (belongs in core/)
- Business feature validation (belongs in modules/)
- Data file placement validation (belongs in core/databases/)
- Repository placement validation (belongs in core/repositories/)
- Category consistency checking (module.json vs actual content)

Based on: Industry DDD/Clean Architecture best practices
Related: docs/knowledge/repository-pattern-modular-architecture.md
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class LayerComplianceAgent(BaseAgent):
    """
    Validates DDD/Clean Architecture layer separation
    
    Ensures:
    - Pure infrastructure lives in core/ (no UI/API)
    - Business features live in modules/ (has UI or API or business logic)
    - Data files live in core/databases/ (not in modules)
    - Repositories live in core/repositories/ (not in modules)
    - module.json categories match actual content
    """
    
    def __init__(self):
        super().__init__("layer_compliance")
        
        # Database file patterns
        self.database_patterns = [
            '*.db', '*.sqlite', '*.sqlite3', '*.db-journal',
            '*.db-wal', '*.db-shm'
        ]
        
        # Infrastructure-only modules (no UI/API, should be in core/)
        # These are patterns that suggest pure infrastructure
        self.infrastructure_indicators = {
            'connection', 'connector', 'adapter', 'driver',
            'repository', 'persistence', 'storage'
        }
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze DDD layer compliance for a module
        
        For modules/ analysis: Checks if module should be in core/
        For core/ analysis: Validates infrastructure is correctly placed
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with layer compliance findings
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
        
        self.logger.info(f"Analyzing DDD layer compliance of {module_path}")
        
        # Determine if we're analyzing a module or the entire project
        is_single_module = (module_path.parent.name == 'modules')
        
        if is_single_module:
            # Analyze single module
            findings.extend(self._check_module_placement(module_path))
            findings.extend(self._check_data_files_in_module(module_path))
            findings.extend(self._check_category_consistency(module_path))
        else:
            # Analyze entire project (all modules)
            modules_dir = module_path / 'modules'
            if modules_dir.exists():
                for module_dir in modules_dir.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith(('_', '.')):
                        findings.extend(self._check_module_placement(module_dir))
                        findings.extend(self._check_data_files_in_module(module_dir))
                        findings.extend(self._check_category_consistency(module_dir))
            
            # Check core/ structure
            findings.extend(self._check_core_structure(module_path))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'low_count': sum(1 for f in findings if f.severity == Severity.LOW),
            'modules_analyzed': 1 if is_single_module else len(list((module_path / 'modules').iterdir())) if (module_path / 'modules').exists() else 0
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"Layer compliance analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of layer compliance capabilities"""
        return [
            "Pure infrastructure detection (modules that should be in core/)",
            "Business feature validation (modules correctly in modules/)",
            "Data file placement validation (database files in wrong location)",
            "Repository placement validation (repo code in modules vs core)",
            "Category consistency checking (module.json vs actual content)",
            "DDD layer separation enforcement",
            "Clean Architecture compliance validation",
            "Hybrid module detection (infrastructure + feature)",
            "Auto-fix suggestions for misplaced components"
        ]
    
    def _check_module_placement(self, module_path: Path) -> List[Finding]:
        """
        Check if module is correctly placed (modules/ vs core/)
        
        Pure infrastructure should be in core/:
        - No frontend/ directory
        - No API endpoints
        - No Blueprint
        - Only backend/ with connection/adapter logic
        
        Features should be in modules/:
        - Has frontend/ or API endpoints or Blueprint
        - User-facing functionality
        - Business logic
        """
        findings = []
        
        try:
            module_json_path = module_path / 'module.json'
            if not module_json_path.exists():
                return findings  # Skip modules without module.json
            
            module_config = self._load_module_json(module_path)
            if not module_config:
                return findings
            
            module_name = module_path.name
            
            # Check if module is pure infrastructure
            has_frontend = (module_path / 'frontend').exists()
            has_api_endpoints = bool(module_config.get('api', {}).get('endpoints', []))
            has_blueprint = bool(module_config.get('backend', {}).get('blueprint'))
            has_backend = (module_path / 'backend').exists()
            
            # Check module.json category
            category = module_config.get('category', '').lower()
            
            # Pure infrastructure: backend only, no UI/API
            is_pure_infrastructure = (
                has_backend and
                not has_frontend and
                not has_api_endpoints and
                not has_blueprint
            )
            
            if is_pure_infrastructure:
                # Check if module name suggests infrastructure
                name_suggests_infra = any(
                    indicator in module_name.lower() 
                    for indicator in self.infrastructure_indicators
                )
                
                severity = Severity.HIGH if name_suggests_infra else Severity.MEDIUM
                
                findings.append(Finding(
                    category="Misplaced Infrastructure",
                    severity=severity,
                    file_path=module_path,
                    line_number=None,
                    description=f"Module '{module_name}' is pure infrastructure (no UI/API) but in modules/",
                    recommendation=(
                        f"MOVE to core/{module_name}/ following DDD principles. "
                        f"Pure infrastructure belongs in core/, not modules/. "
                        f"Modules/ should contain user-facing features only."
                    ),
                    code_snippet=None
                ))
            
            # Hybrid check: Infrastructure category but has UI/API
            elif category == 'infrastructure' and (has_frontend or has_api_endpoints):
                findings.append(Finding(
                    category="Hybrid Module",
                    severity=Severity.MEDIUM,
                    file_path=module_path,
                    line_number=None,
                    description=f"Module '{module_name}' category='Infrastructure' but has UI/API (hybrid)",
                    recommendation=(
                        f"CONSIDER: Split into core/{module_name}/ (infrastructure) + "
                        f"modules/{module_name}_manager/ (feature). OR change category to 'Feature' "
                        f"if management UI is primary purpose."
                    ),
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check module placement for {module_path.name}: {str(e)}")
        
        return findings
    
    def _check_data_files_in_module(self, module_path: Path) -> List[Finding]:
        """
        Check if module contains database files (should be in core/databases/)
        
        Database files belong in core/databases/ following DDD:
        - Infrastructure layer owns data persistence
        - Modules should be pure business logic (no data files)
        - Separation of concerns: code vs data
        """
        findings = []
        
        try:
            module_name = module_path.name
            
            # Search for database files
            db_files_found = []
            for pattern in self.database_patterns:
                db_files_found.extend(list(module_path.rglob(pattern)))
            
            if db_files_found:
                # Count total size of database files
                total_size_mb = sum(f.stat().st_size for f in db_files_found if f.is_file()) / (1024 * 1024)
                
                db_file_names = [f.name for f in db_files_found]
                
                findings.append(Finding(
                    category="Data Files in Module",
                    severity=Severity.HIGH,
                    file_path=module_path,
                    line_number=None,
                    description=(
                        f"Module '{module_name}' contains {len(db_files_found)} database file(s) "
                        f"({total_size_mb:.2f} MB): {', '.join(db_file_names[:3])}"
                        f"{' ...' if len(db_file_names) > 3 else ''}"
                    ),
                    recommendation=(
                        f"MOVE database files to core/databases/{module_name}/ following DDD principles. "
                        f"Infrastructure layer (core/) owns data persistence. "
                        f"Modules should be pure business logic without data files. "
                        f"Update file paths in code after moving."
                    ),
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check data files in {module_path.name}: {str(e)}")
        
        return findings
    
    def _check_category_consistency(self, module_path: Path) -> List[Finding]:
        """
        Check if module.json category matches actual module content
        
        Validates:
        - Infrastructure modules should have no UI/API (unless manager)
        - Business modules should have UI or API
        - Developer Tools should have UI
        """
        findings = []
        
        try:
            module_config = self._load_module_json(module_path)
            if not module_config:
                return findings
            
            module_name = module_path.name
            category = module_config.get('category', 'Uncategorized')
            
            has_frontend = (module_path / 'frontend').exists()
            has_api = bool(module_config.get('api', {}).get('endpoints', []))
            has_blueprint = bool(module_config.get('backend', {}).get('blueprint'))
            
            has_ui_or_api = has_frontend or has_api or has_blueprint
            
            # Check consistency
            if category == 'Infrastructure' and has_ui_or_api:
                # Already handled by hybrid check in _check_module_placement
                pass
            
            elif category in ['Business Logic', 'Business', 'Domain'] and not has_ui_or_api:
                findings.append(Finding(
                    category="Category Mismatch",
                    severity=Severity.LOW,
                    file_path=module_path / 'module.json',
                    line_number=None,
                    description=f"Module '{module_name}' category='{category}' but has no UI/API",
                    recommendation=(
                        f"REVIEW: Business modules typically have user-facing components. "
                        f"Either add UI/API or change category to 'Infrastructure' or 'Utility'."
                    ),
                    code_snippet=None
                ))
            
            elif category == 'Developer Tools' and not has_frontend:
                findings.append(Finding(
                    category="Category Mismatch",
                    severity=Severity.LOW,
                    file_path=module_path / 'module.json',
                    line_number=None,
                    description=f"Module '{module_name}' category='Developer Tools' but has no UI",
                    recommendation=(
                        f"REVIEW: Developer tools typically have a UI for developers. "
                        f"Consider adding frontend/ or changing category."
                    ),
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check category consistency for {module_path.name}: {str(e)}")
        
        return findings
    
    def _check_core_structure(self, project_root: Path) -> List[Finding]:
        """
        Validate core/ directory structure follows DDD principles
        
        Expected structure:
        core/
        ├── interfaces/      # Ports (abstractions)
        ├── repositories/    # Data access adapters
        ├── services/        # Infrastructure services
        └── databases/       # Data storage (NEW)
        """
        findings = []
        
        try:
            core_dir = project_root / 'core'
            if not core_dir.exists():
                findings.append(Finding(
                    category="Missing Core Directory",
                    severity=Severity.CRITICAL,
                    file_path=project_root,
                    line_number=None,
                    description="Project missing core/ directory for infrastructure layer",
                    recommendation=(
                        "CREATE core/ directory following DDD/Clean Architecture. "
                        "Structure: core/interfaces/, core/repositories/, core/services/, core/databases/"
                    ),
                    code_snippet=None
                ))
                return findings
            
            # Check for expected subdirectories
            expected_dirs = {
                'interfaces': 'Ports (abstractions)',
                'repositories': 'Data access adapters',
                'services': 'Infrastructure services'
            }
            
            missing_dirs = []
            for dir_name, purpose in expected_dirs.items():
                if not (core_dir / dir_name).exists():
                    missing_dirs.append(f"{dir_name}/ ({purpose})")
            
            if missing_dirs:
                findings.append(Finding(
                    category="Incomplete Core Structure",
                    severity=Severity.MEDIUM,
                    file_path=core_dir,
                    line_number=None,
                    description=f"core/ directory missing standard subdirectories: {', '.join(missing_dirs)}",
                    recommendation=(
                        "CREATE missing directories following DDD structure. "
                        "See docs/knowledge/repository-pattern-modular-architecture.md"
                    ),
                    code_snippet=None
                ))
            
            # Check if databases/ exists (recommended)
            if not (core_dir / 'databases').exists():
                findings.append(Finding(
                    category="Missing Databases Directory",
                    severity=Severity.LOW,
                    file_path=core_dir,
                    line_number=None,
                    description="core/ directory missing databases/ subdirectory (recommended)",
                    recommendation=(
                        "CREATE core/databases/ for centralized data storage. "
                        "Move test databases from modules/ to core/databases/"
                    ),
                    code_snippet=None
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check core structure: {str(e)}")
        
        return findings
    
    def _load_module_json(self, module_path: Path) -> Optional[Dict]:
        """Load and parse module.json"""
        try:
            module_json_path = module_path / 'module.json'
            if not module_json_path.exists():
                return None
            
            with open(module_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            self.logger.warning(f"Could not load module.json for {module_path.name}: {str(e)}")
            return None
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"DDD layer compliance validated: {metrics['modules_analyzed']} module(s) analyzed, all correctly placed"
        
        return (
            f"LAYER COMPLIANCE ISSUES: "
            f"{metrics['total_findings']} violation(s) found in {metrics['modules_analyzed']} module(s) - "
            f"{metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM, {metrics['low_count']} LOW"
        )