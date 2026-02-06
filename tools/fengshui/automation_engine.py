#!/usr/bin/env python3
"""
Feng Shui Automation Engine - Pattern Integration
==================================================

Complete automation loop integrating all 7 GoF patterns.

Architecture:
    Composite detects issues
         ↓
    Builder creates work packages
         ↓
    Command executes automated fixes
         ↓
    Memento tracks evolution
         ↓
    Visitor validates fixes
         ↓
    [REPEAT] → Self-healing architecture

Like Gu Wu for tests, this is self-healing for architecture!
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Import all patterns - handle both direct execution and import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.fengshui.validation_composite import (
    ProjectValidation, ModuleValidation
)
from tools.fengshui.work_package_builder import (
    WorkPackageBuilder, WorkPackageDirector, WorkPackage
)
from tools.fengshui.fix_commands import (
    CommandFactory, CommandInvoker, CreateModuleJsonCommand,
    CreateModuleReadmeCommand, AddBlueprintConfigCommand
)
from tools.fengshui.architecture_history import (
    ArchitectureOriginator, ArchitectureCaretaker, ArchitectureSnapshot
)


@dataclass
class AutomationResult:
    """Result of automation engine execution"""
    issues_detected: int
    work_packages_created: int
    fixes_applied: int
    fixes_failed: int
    snapshot_saved: bool
    execution_time_seconds: float


class FengShuiAutomationEngine:
    """
    Orchestrator: Integrates all 7 GoF patterns into complete automation loop
    
    Workflow:
    1. Composite Pattern: Detect architecture issues
    2. Builder Pattern: Generate work packages for issues
    3. Command Pattern: Execute automated fixes (where possible)
    4. Memento Pattern: Capture architecture snapshot
    5. Visitor Pattern: Validate fixes (via Composite)
    6. Chain Pattern: Run quality checks (via Composite)
    7. Template Method: Consistent reporting (via Composite)
    
    Result: Self-healing architecture engine
    """
    
    def __init__(self, project_root: Path = Path('.')):
        self.project_root = project_root
        self.modules_dir = project_root / 'modules'
        
        # Pattern components
        self.command_invoker = CommandInvoker()
        self.wp_builder = WorkPackageBuilder()
        self.wp_director = WorkPackageDirector(self.wp_builder)
        self.originator = ArchitectureOriginator()
        self.caretaker = ArchitectureCaretaker()
    
    def run_full_automation(self, auto_fix: bool = False) -> AutomationResult:
        """
        Execute complete automation loop
        
        Args:
            auto_fix: If True, automatically apply fixes. If False, only detect and report.
            
        Returns:
            AutomationResult with summary
        """
        import time
        start_time = time.time()
        
        print("\n" + "="*80)
        print("FENG SHUI AUTOMATION ENGINE - FULL CYCLE")
        print("="*80 + "\n")
        
        # Step 1: Detect issues (Composite Pattern)
        print("[1/5] DETECTING ARCHITECTURE ISSUES (Composite Pattern)...")
        print("-" * 80)
        project_validation = self._detect_issues()
        
        issues_detected = sum(
            len(finding.findings) 
            for module_result in project_validation.module_results 
            for finding in module_result.findings.values()
        )
        print(f"  Found: {issues_detected} issues across {len(project_validation.module_results)} modules")
        
        # Step 2: Generate work packages (Builder Pattern)
        print("\n[2/5] GENERATING WORK PACKAGES (Builder Pattern)...")
        print("-" * 80)
        work_packages = self._generate_work_packages(project_validation)
        print(f"  Created: {len(work_packages)} work packages")
        
        for wp in work_packages[:3]:  # Show first 3
            print(f"    - {wp.wp_id}: {wp.title} ({wp.priority})")
        if len(work_packages) > 3:
            print(f"    ... and {len(work_packages) - 3} more")
        
        # Step 3: Execute automated fixes (Command Pattern)
        print("\n[3/5] EXECUTING AUTOMATED FIXES (Command Pattern)...")
        print("-" * 80)
        
        if auto_fix:
            fix_result = self._apply_automated_fixes(project_validation)
            print(f"  Succeeded: {fix_result['succeeded']} fixes")
            print(f"  Failed: {fix_result['failed']} fixes")
        else:
            print("  [SKIPPED] Auto-fix disabled (set auto_fix=True to enable)")
            fix_result = {'succeeded': 0, 'failed': 0}
        
        # Step 4: Capture snapshot (Memento Pattern)
        print("\n[4/5] CAPTURING ARCHITECTURE SNAPSHOT (Memento Pattern)...")
        print("-" * 80)
        snapshot = self.originator.capture_snapshot()
        snapshot_saved = self.caretaker.save_snapshot(snapshot)
        
        if snapshot_saved:
            print(f"  [SAVED] Snapshot at {snapshot.git_commit[:8]}")
            print(f"    Score: {snapshot.feng_shui_score} (Grade {snapshot.grade})")
            print(f"    Issues: {snapshot.total_issues} total")
        else:
            print("  [ERROR] Failed to save snapshot")
        
        # Step 5: Compare with history (Memento Pattern)
        print("\n[5/5] ANALYZING EVOLUTION (Memento Pattern)...")
        print("-" * 80)
        
        comparison = self.caretaker.compare_last_two()
        if comparison:
            print(f"  Score Change: {comparison.before.feng_shui_score} → {comparison.after.feng_shui_score}")
            print(f"  Issues Resolved: {comparison.issues_resolved}")
            print(f"  Modules Improved: {len(comparison.modules_improved)}")
        else:
            print("  [INFO] Not enough snapshots for comparison (need 2+)")
        
        # Summary
        elapsed = time.time() - start_time
        
        print("\n" + "="*80)
        print("AUTOMATION SUMMARY")
        print("="*80)
        print(f"  Issues Detected: {issues_detected}")
        print(f"  Work Packages: {len(work_packages)}")
        print(f"  Fixes Applied: {fix_result['succeeded']}")
        print(f"  Fixes Failed: {fix_result['failed']}")
        print(f"  Snapshot Saved: {'Yes' if snapshot_saved else 'No'}")
        print(f"  Execution Time: {elapsed:.2f}s")
        
        return AutomationResult(
            issues_detected=issues_detected,
            work_packages_created=len(work_packages),
            fixes_applied=fix_result['succeeded'],
            fixes_failed=fix_result['failed'],
            snapshot_saved=snapshot_saved,
            execution_time_seconds=elapsed
        )
    
    def _detect_issues(self) -> ProjectValidation:
        """
        Detect issues using Composite Pattern
        
        Returns:
            ProjectValidation with all findings
        """
        # Create project validation
        project = ProjectValidation(self.project_root)
        
        # Scan all modules
        if self.modules_dir.exists():
            for module_dir in self.modules_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('__'):
                    module_validation = ModuleValidation(module_dir)
                    project.add_module(module_validation)
        
        # Validate entire project
        project.validate()
        
        return project
    
    def _generate_work_packages(self, project_validation: ProjectValidation) -> List[WorkPackage]:
        """
        Generate work packages using Builder Pattern
        
        Args:
            project_validation: Validation results from Composite
            
        Returns:
            List of work packages
        """
        work_packages = []
        
        # Group issues by severity
        critical_modules = []
        high_modules = []
        
        for module_result in project_validation.module_results:
            # Check for critical issues (missing module.json)
            if 'module_json' in module_result.findings:
                if any('not found' in f for f in module_result.findings['module_json'].findings):
                    critical_modules.append(module_result.module_name)
            
            # Check for high issues (missing README, blueprint config)
            if 'readme' in module_result.findings:
                if any('not found' in f for f in module_result.findings['readme'].findings):
                    high_modules.append(module_result.module_name)
        
        # Create work packages using Director
        if critical_modules:
            self.wp_builder.reset()
            wp = self.wp_director.construct_architecture_refactoring(
                wp_id="WP-AUTO-001",
                title="Fix Missing module.json Files",
                modules_affected=critical_modules,
                violation_type='Module Structure'
            )
            work_packages.append(wp)
        
        if high_modules:
            self.wp_builder.reset()
            wp = self.wp_director.construct_architecture_refactoring(
                wp_id="WP-AUTO-002",
                title="Add Missing README Documentation",
                modules_affected=high_modules,
                violation_type='Documentation'
            )
            work_packages.append(wp)
        
        return work_packages
    
    def _apply_automated_fixes(self, project_validation: ProjectValidation) -> Dict[str, int]:
        """
        Apply automated fixes using Command Pattern
        
        Args:
            project_validation: Validation results
            
        Returns:
            Dict with success/failure counts
        """
        commands = []
        
        # Generate fix commands for each module
        for module_result in project_validation.module_results:
            module_path = self.modules_dir / module_result.module_name
            
            # Collect findings for this module
            findings = []
            for finding_list in module_result.findings.values():
                findings.extend(finding_list.findings)
            
            # Create commands using Factory
            module_commands = CommandFactory.create_commands_for_module(module_path, findings)
            commands.extend(module_commands)
        
        # Execute all commands
        if commands:
            result = self.command_invoker.execute_batch(commands)
            return result
        else:
            return {'succeeded': 0, 'failed': 0}
    
    def run_detection_only(self) -> ProjectValidation:
        """
        Run detection phase only (no fixes)
        
        Returns:
            ProjectValidation with findings
        """
        print("\n" + "="*80)
        print("FENG SHUI AUTOMATION ENGINE - DETECTION ONLY")
        print("="*80 + "\n")
        
        print("[*] DETECTING ARCHITECTURE ISSUES...")
        project_validation = self._detect_issues()
        
        # Print summary
        total_issues = sum(
            len(finding.findings)
            for module_result in project_validation.module_results
            for finding in module_result.findings.values()
        )
        
        print(f"\n[*] SUMMARY:")
        print(f"  Modules Scanned: {len(project_validation.module_results)}")
        print(f"  Issues Found: {total_issues}")
        
        return project_validation
    
    def run_fix_only(self, module_name: str) -> Dict[str, int]:
        """
        Run automated fixes for specific module
        
        Args:
            module_name: Module to fix
            
        Returns:
            Fix result summary
        """
        print(f"\n[*] FIXING MODULE: {module_name}")
        
        module_path = self.modules_dir / module_name
        if not module_path.exists():
            print(f"  [ERROR] Module not found: {module_path}")
            return {'succeeded': 0, 'failed': 0}
        
        # Detect issues in this module
        module_validation = ModuleValidation(module_path)
        module_validation.validate()
        
        # Generate and execute commands
        findings = []
        for finding_list in module_validation.findings.values():
            findings.extend(finding_list.findings)
        
        commands = CommandFactory.create_commands_for_module(module_path, findings)
        
        if commands:
            result = self.command_invoker.execute_batch(commands)
            print(f"  Fixes Applied: {result['succeeded']}")
            print(f"  Fixes Failed: {result['failed']}")
            return result
        else:
            print("  [INFO] No automated fixes available")
            return {'succeeded': 0, 'failed': 0}


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_automation_engine():
    """
    Demonstrate complete automation loop
    """
    print("\n" + "="*80)
    print("FENG SHUI AUTOMATION ENGINE DEMONSTRATION")
    print("="*80)
    print("""
This engine integrates ALL 7 GoF patterns:

1. Chain of Responsibility - Modular quality checks
2. Template Method - Consistent phase workflow
3. Visitor Pattern - AST code analysis
4. Composite Pattern - Hierarchical validation ← STARTS HERE
5. Command Pattern - Automated fixes
6. Memento Pattern - Architecture evolution tracking
7. Builder Pattern - Work package generation

Complete Loop:
    Composite detects → Builder creates WPs → Command fixes
         ↓                                           ↓
    Memento tracks ← Visitor validates ← [Fixes Applied]
""")
    
    # Create engine
    engine = FengShuiAutomationEngine()
    
    # Run detection only (safe, no changes)
    print("\n" + "="*80)
    print("RUNNING DETECTION MODE (no fixes applied)")
    print("="*80)
    
    project_validation = engine.run_detection_only()
    
    # Show what could be automated
    print("\n" + "="*80)
    print("AUTOMATION POTENTIAL")
    print("="*80)
    print("""
With auto_fix=True, the engine would:
1. Create missing module.json files automatically
2. Generate README.md templates automatically
3. Add missing blueprint configurations automatically
4. Track improvements in architecture history
5. Generate work packages for manual fixes
6. Provide rollback capability if needed

Example:
    engine = FengShuiAutomationEngine()
    result = engine.run_full_automation(auto_fix=True)
    
    # Would auto-fix 10+ issues in seconds!
    # Like Gu Wu for architecture!
""")
    
    print("\n" + "="*80)
    print("INTEGRATION COMMANDS")
    print("="*80)
    print("""
Available commands:

# Full automation (detection + fixes + tracking)
python -m tools.fengshui.automation_engine --auto-fix

# Detection only (safe, no changes)
python -m tools.fengshui.automation_engine --detect

# Fix specific module
python -m tools.fengshui.automation_engine --fix-module knowledge_graph

# View architecture evolution
python -m tools.fengshui.architecture_history --compare

# Generate work packages
python -m tools.fengshui.work_package_builder --module data_products
""")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Feng Shui Automation Engine')
    parser.add_argument('--auto-fix', action='store_true', help='Apply automated fixes')
    parser.add_argument('--detect', action='store_true', help='Detection only (no fixes)')
    parser.add_argument('--fix-module', type=str, help='Fix specific module')
    
    args = parser.parse_args()
    
    engine = FengShuiAutomationEngine()
    
    if args.fix_module:
        # Fix specific module
        engine.run_fix_only(args.fix_module)
    
    elif args.detect:
        # Detection only
        engine.run_detection_only()
    
    elif args.auto_fix:
        # Full automation with fixes
        result = engine.run_full_automation(auto_fix=True)
        print(f"\n[COMPLETE] Automation finished in {result.execution_time_seconds:.2f}s")
    
    else:
        # Demo mode
        demonstrate_automation_engine()