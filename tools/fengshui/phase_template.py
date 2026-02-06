#!/usr/bin/env python3
"""
Feng Shui Phase Template - Template Method Pattern
===================================================

Base class for Feng Shui phase execution with consistent workflow.

GoF Pattern: Template Method
- Defines common workflow for all phases
- Each phase implements specific analysis logic
- Consistent reporting and work package generation
"""
import sys
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class Finding:
    """A single finding from phase analysis"""
    title: str
    description: str
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    file_path: str = ""
    line_number: int = 0
    suggestion: str = ""


@dataclass
class WorkPackage:
    """A work package generated from findings"""
    id: str
    title: str
    description: str
    priority: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    effort_hours: float
    findings: List[Finding]
    status: str = "PLANNED"


class FengShuiPhase(ABC):
    """
    Abstract base class for Feng Shui phases (Template Method pattern)
    
    Defines the workflow all phases follow:
    1. Analyze codebase/files
    2. Detect issues
    3. Generate work packages
    4. Create report
    
    Each phase implements specific analysis logic.
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize phase
        
        Args:
            project_root: Root directory of project (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.findings: List[Finding] = []
        self.work_packages: List[WorkPackage] = []
    
    def execute(self) -> Tuple[bool, Dict]:
        """
        Execute the complete phase workflow (Template Method)
        
        This is the template method that defines the algorithm skeleton.
        Subclasses CANNOT override this - they implement the hooks instead.
        
        Returns:
            (success, results_dict) - success=True if no CRITICAL findings
        """
        print(f"\n{'='*80}")
        print(f"FENG SHUI PHASE: {self.phase_name}")
        print(f"{'='*80}\n")
        
        # Step 1: Analyze (hook method)
        print(f"[1/4] Analyzing {self.analysis_target}...")
        self.analyze()
        
        # Step 2: Detect issues (hook method)
        print(f"[2/4] Detecting issues...")
        self.detect_issues()
        
        # Step 3: Generate work packages (hook method)
        print(f"[3/4] Generating work packages...")
        self.generate_work_packages()
        
        # Step 4: Create report (concrete method - same for all phases)
        print(f"[4/4] Creating report...")
        report = self._create_report()
        
        # Determine success
        critical_count = sum(1 for f in self.findings if f.severity == 'CRITICAL')
        success = critical_count == 0
        
        return success, report
    
    @property
    @abstractmethod
    def phase_name(self) -> str:
        """Human-readable phase name"""
        pass
    
    @property
    @abstractmethod
    def analysis_target(self) -> str:
        """What this phase analyzes (e.g., 'scripts', 'documentation')"""
        pass
    
    @abstractmethod
    def analyze(self):
        """
        Step 1: Analyze the codebase/files
        
        Gather data needed for issue detection.
        Store results in self attributes for later use.
        """
        pass
    
    @abstractmethod
    def detect_issues(self):
        """
        Step 2: Detect issues based on analysis
        
        Add findings to self.findings list.
        Each finding should have clear description and severity.
        """
        pass
    
    @abstractmethod
    def generate_work_packages(self):
        """
        Step 3: Generate work packages from findings
        
        Group related findings into actionable work packages.
        Add to self.work_packages list.
        """
        pass
    
    def _create_report(self) -> Dict:
        """
        Step 4: Create standardized report (concrete method)
        
        This is the same for all phases - formats findings and work packages.
        
        Returns:
            Report dictionary with findings, work packages, summary
        """
        # Count by severity
        critical = [f for f in self.findings if f.severity == 'CRITICAL']
        high = [f for f in self.findings if f.severity == 'HIGH']
        medium = [f for f in self.findings if f.severity == 'MEDIUM']
        low = [f for f in self.findings if f.severity == 'LOW']
        
        # Print summary
        print(f"\nRESULTS:")
        print(f"  CRITICAL: {len(critical)}")
        print(f"  HIGH: {len(high)}")
        print(f"  MEDIUM: {len(medium)}")
        print(f"  LOW: {len(low)}")
        print(f"  Total Findings: {len(self.findings)}")
        print(f"  Work Packages: {len(self.work_packages)}")
        
        # Print findings by severity
        if critical:
            print(f"\nCRITICAL ISSUES:")
            for i, finding in enumerate(critical, 1):
                print(f"  {i}. {finding.title}")
                if finding.file_path:
                    print(f"     File: {finding.file_path}")
        
        if high:
            print(f"\nHIGH PRIORITY:")
            for i, finding in enumerate(high, 1):
                print(f"  {i}. {finding.title}")
        
        # Print work packages
        if self.work_packages:
            print(f"\nWORK PACKAGES:")
            total_effort = sum(wp.effort_hours for wp in self.work_packages)
            for wp in self.work_packages:
                print(f"  {wp.id}: {wp.title}")
                print(f"    Priority: {wp.priority} | Effort: {wp.effort_hours}h")
            print(f"\n  Total Effort: {total_effort} hours")
        
        # Phase result
        if critical:
            print(f"\n{'='*80}")
            print(f"PHASE RESULT: CRITICAL ISSUES FOUND")
            print(f"{'='*80}\n")
        elif high:
            print(f"\n{'='*80}")
            print(f"PHASE RESULT: HIGH PRIORITY WORK NEEDED")
            print(f"{'='*80}\n")
        else:
            print(f"\n{'='*80}")
            print(f"PHASE RESULT: PASSED")
            print(f"{'='*80}\n")
        
        return {
            'phase': self.phase_name,
            'findings': {
                'critical': len(critical),
                'high': len(high),
                'medium': len(medium),
                'low': len(low),
                'total': len(self.findings)
            },
            'work_packages': len(self.work_packages),
            'total_effort_hours': sum(wp.effort_hours for wp in self.work_packages),
            'findings_list': self.findings,
            'work_packages_list': self.work_packages
        }


class QualityGatePhase(FengShuiPhase):
    """
    Phase 3: Quality validation using Chain of Responsibility pattern
    
    This phase demonstrates integration of both GoF patterns:
    - Template Method (this class) defines workflow
    - Chain of Responsibility (quality_check.py) performs checks
    """
    
    @property
    def phase_name(self) -> str:
        return "Quality Gate Validation"
    
    @property
    def analysis_target(self) -> str:
        return "all modules"
    
    def analyze(self):
        """Discover all modules in modules/ directory"""
        self.modules_dir = self.project_root / 'modules'
        
        if not self.modules_dir.exists():
            self.findings.append(Finding(
                title="No modules/ directory found",
                description="Project should have modules/ directory with modular components",
                severity='CRITICAL'
            ))
            self.modules = []
            return
        
        # Find all module directories
        self.modules = [
            d for d in self.modules_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.') and d.name != '__pycache__'
        ]
        
        print(f"  Found {len(self.modules)} modules")
    
    def detect_issues(self):
        """Run quality checks on each module"""
        from tools.fengshui.quality_check import build_quality_check_chain, ModuleContext
        import json
        
        failing_modules = []
        
        for module_dir in self.modules:
            # Load module config
            config_file = module_dir / 'module.json'
            if not config_file.exists():
                self.findings.append(Finding(
                    title=f"Module {module_dir.name} missing module.json",
                    description="All modules must have module.json configuration",
                    severity='HIGH',
                    file_path=str(module_dir)
                ))
                failing_modules.append(module_dir.name)
                continue
            
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                self.findings.append(Finding(
                    title=f"Module {module_dir.name} has invalid module.json",
                    description="module.json must be valid JSON",
                    severity='HIGH',
                    file_path=str(config_file)
                ))
                failing_modules.append(module_dir.name)
                continue
            
            # Create context
            context = ModuleContext(
                module_path=module_dir,
                module_name=module_dir.name,
                has_backend=(module_dir / 'backend').exists(),
                config=config
            )
            
            # Run quality check chain
            chain = build_quality_check_chain()
            results = chain.check(context)
            
            # Convert results to findings
            errors = [r for r in results if r.severity == 'ERROR' and not r.passed]
            
            if errors:
                failing_modules.append(module_dir.name)
                for error in errors:
                    self.findings.append(Finding(
                        title=f"{module_dir.name}: {error.check_name} failed",
                        description=error.message,
                        severity='HIGH',
                        file_path=str(module_dir)
                    ))
        
        if failing_modules:
            print(f"  {len(failing_modules)} modules failing quality gate")
        else:
            print(f"  All {len(self.modules)} modules passed!")
    
    def generate_work_packages(self):
        """Group findings by module into work packages"""
        if not self.findings:
            return
        
        # Group by module
        by_module: Dict[str, List[Finding]] = {}
        for finding in self.findings:
            # Extract module name from file_path
            if 'modules/' in finding.file_path:
                module = finding.file_path.split('modules/')[1].split('/')[0]
            else:
                module = 'general'
            
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(finding)
        
        # Create work packages
        for i, (module, findings) in enumerate(by_module.items(), 1):
            # Estimate effort (30 min per finding, min 1 hour)
            effort = max(1.0, len(findings) * 0.5)
            
            # Determine priority from findings
            has_high = any(f.severity == 'HIGH' for f in findings)
            priority = 'HIGH' if has_high else 'MEDIUM'
            
            self.work_packages.append(WorkPackage(
                id=f"WP-QG-{i:03d}",
                title=f"Fix quality gate violations in {module}",
                description=f"Address {len(findings)} issues in {module} module",
                priority=priority,
                effort_hours=effort,
                findings=findings
            ))


# Example usage
if __name__ == '__main__':
    # Add project root to Python path for imports
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    phase = QualityGatePhase()
    success, report = phase.execute()
    
    sys.exit(0 if success else 1)
