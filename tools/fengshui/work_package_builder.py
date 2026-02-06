#!/usr/bin/env python3
"""
Feng Shui Work Package Builder - Builder Pattern
=================================================

Consistent construction of complex work packages.

GoF Pattern: Builder
- Step-by-step construction of complex objects
- Fluent interface for readability
- Automatic effort estimation
- Consistent validation and formatting
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class WorkPackage:
    """
    Complete work package specification
    
    Contains all information needed to execute and track work:
    - Identification (ID, title)
    - Scope (goal, problem, solution)
    - Planning (priority, effort, dependencies)
    - Tracking (status, completion checklist)
    """
    wp_id: str
    title: str
    goal: str
    problem: str
    solution: str
    priority: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    effort_hours: float
    findings: List[str] = field(default_factory=list)
    implementation_steps: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    trade_offs: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def format_markdown(self) -> str:
        """
        Format work package as PROJECT_TRACKER.md entry
        
        Returns:
            Markdown-formatted work package
        """
        priority_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟡',
            'MEDIUM': '🟢',
            'LOW': '⚪'
        }
        
        md = []
        md.append(f"#### {self.wp_id}: {self.title} {priority_emoji.get(self.priority, '')} {self.priority}")
        md.append(f"**Goal**: {self.goal}\n")
        
        md.append(f"**Problem**: {self.problem}\n")
        md.append(f"**Solution**: {self.solution}\n")
        
        if self.findings:
            md.append("**Findings**:")
            for finding in self.findings:
                md.append(f"- {finding}")
            md.append("")
        
        if self.implementation_steps:
            md.append(f"**Implementation Plan** ({self.effort_hours} hours):")
            for i, step in enumerate(self.implementation_steps, 1):
                md.append(f"{i}. {step}")
            md.append("")
        
        if self.benefits:
            md.append("**Benefits**:")
            for benefit in self.benefits:
                md.append(f"- ✅ {benefit}")
            md.append("")
        
        if self.trade_offs:
            md.append("**Trade-offs**:")
            for trade_off in self.trade_offs:
                md.append(f"- ⚠️ {trade_off}")
            md.append("")
        
        if self.dependencies:
            md.append("**Dependencies**:")
            for dep in self.dependencies:
                md.append(f"- {dep}")
            md.append("")
        
        if self.references:
            md.append("**References**:")
            for ref in self.references:
                md.append(f"- {ref}")
            md.append("")
        
        md.append(f"**Effort**: {self.effort_hours} hours")
        md.append(f"**Priority**: {priority_emoji.get(self.priority, '')} {self.priority}")
        md.append(f"**Status**: 📋 Planned")
        
        return "\n".join(md)


class WorkPackageBuilder:
    """
    Builder: Constructs work packages step-by-step (Builder pattern)
    
    Fluent interface for readable construction:
    ```python
    wp = (WorkPackageBuilder()
          .set_id("WP-001")
          .set_title("Fix DI Violations")
          .set_priority("HIGH")
          .add_finding("10/12 modules failing")
          .estimate_effort()  # Auto-calculate
          .build())
    ```
    """
    
    def __init__(self):
        self._wp_id: Optional[str] = None
        self._title: Optional[str] = None
        self._goal: Optional[str] = None
        self._problem: Optional[str] = None
        self._solution: Optional[str] = None
        self._priority: str = 'MEDIUM'
        self._effort_hours: Optional[float] = None
        self._findings: List[str] = []
        self._implementation_steps: List[str] = []
        self._dependencies: List[str] = []
        self._benefits: List[str] = []
        self._trade_offs: List[str] = []
        self._references: List[str] = []
        self._metadata: Dict[str, Any] = {}
    
    def set_id(self, wp_id: str) -> 'WorkPackageBuilder':
        """Set work package ID (e.g., 'WP-FS-001')"""
        self._wp_id = wp_id
        return self
    
    def set_title(self, title: str) -> 'WorkPackageBuilder':
        """Set work package title"""
        self._title = title
        return self
    
    def set_goal(self, goal: str) -> 'WorkPackageBuilder':
        """Set goal (what we want to achieve)"""
        self._goal = goal
        return self
    
    def set_problem(self, problem: str) -> 'WorkPackageBuilder':
        """Set problem description"""
        self._problem = problem
        return self
    
    def set_solution(self, solution: str) -> 'WorkPackageBuilder':
        """Set solution approach"""
        self._solution = solution
        return self
    
    def set_priority(self, priority: str) -> 'WorkPackageBuilder':
        """Set priority: CRITICAL, HIGH, MEDIUM, or LOW"""
        valid_priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        self._priority = priority
        return self
    
    def set_effort(self, hours: float) -> 'WorkPackageBuilder':
        """Set effort estimate manually"""
        self._effort_hours = hours
        return self
    
    def add_finding(self, finding: str) -> 'WorkPackageBuilder':
        """Add a specific finding/issue"""
        self._findings.append(finding)
        return self
    
    def add_findings(self, findings: List[str]) -> 'WorkPackageBuilder':
        """Add multiple findings"""
        self._findings.extend(findings)
        return self
    
    def add_step(self, step: str) -> 'WorkPackageBuilder':
        """Add implementation step"""
        self._implementation_steps.append(step)
        return self
    
    def add_steps(self, steps: List[str]) -> 'WorkPackageBuilder':
        """Add multiple implementation steps"""
        self._implementation_steps.extend(steps)
        return self
    
    def add_dependency(self, dependency: str) -> 'WorkPackageBuilder':
        """Add work package dependency"""
        self._dependencies.append(dependency)
        return self
    
    def add_benefit(self, benefit: str) -> 'WorkPackageBuilder':
        """Add expected benefit"""
        self._benefits.append(benefit)
        return self
    
    def add_trade_off(self, trade_off: str) -> 'WorkPackageBuilder':
        """Add trade-off/caveat"""
        self._trade_offs.append(trade_off)
        return self
    
    def add_reference(self, reference: str) -> 'WorkPackageBuilder':
        """Add reference document/guide"""
        self._references.append(reference)
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'WorkPackageBuilder':
        """Add custom metadata"""
        self._metadata[key] = value
        return self
    
    def estimate_effort(self) -> 'WorkPackageBuilder':
        """
        Automatically estimate effort based on complexity
        
        Estimation formula:
        - Base: 1 hour per implementation step
        - +0.5 hours per dependency
        - +1 hour if HIGH/CRITICAL priority
        - Round to nearest 0.5 hours
        """
        if self._effort_hours is not None:
            return self  # Manual estimate already set
        
        # Base effort from steps
        base_effort = len(self._implementation_steps) * 1.0
        
        # Add dependency complexity
        dependency_overhead = len(self._dependencies) * 0.5
        
        # Add priority complexity
        priority_overhead = 1.0 if self._priority in ['HIGH', 'CRITICAL'] else 0.0
        
        # Calculate total
        total = base_effort + dependency_overhead + priority_overhead
        
        # Round to nearest 0.5
        self._effort_hours = round(total * 2) / 2
        
        return self
    
    def validate(self) -> List[str]:
        """
        Validate builder state before building
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self._wp_id:
            errors.append("Work package ID is required")
        if not self._title:
            errors.append("Title is required")
        if not self._goal:
            errors.append("Goal is required")
        if not self._problem:
            errors.append("Problem description is required")
        if not self._solution:
            errors.append("Solution approach is required")
        if self._effort_hours is None or self._effort_hours <= 0:
            errors.append("Effort estimate is required (use estimate_effort() or set_effort())")
        
        return errors
    
    def build(self) -> WorkPackage:
        """
        Build the work package
        
        Returns:
            Complete WorkPackage object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate
        errors = self.validate()
        if errors:
            raise ValueError(f"Cannot build work package:\n" + "\n".join(f"  - {e}" for e in errors))
        
        # Build
        return WorkPackage(
            wp_id=self._wp_id,
            title=self._title,
            goal=self._goal,
            problem=self._problem,
            solution=self._solution,
            priority=self._priority,
            effort_hours=self._effort_hours,
            findings=self._findings,
            implementation_steps=self._implementation_steps,
            dependencies=self._dependencies,
            benefits=self._benefits,
            trade_offs=self._trade_offs,
            references=self._references,
            metadata=self._metadata
        )
    
    def reset(self) -> 'WorkPackageBuilder':
        """Reset builder to initial state for reuse"""
        self.__init__()
        return self


class WorkPackageDirector:
    """
    Director: Orchestrates builder for common work package types
    
    Provides pre-configured builders for:
    - Architecture refactoring WPs
    - Bug fix WPs
    - Feature enhancement WPs
    - Documentation WPs
    """
    
    def __init__(self, builder: WorkPackageBuilder):
        self.builder = builder
    
    def construct_architecture_refactoring(
        self,
        wp_id: str,
        title: str,
        modules_affected: List[str],
        violation_type: str
    ) -> WorkPackage:
        """
        Construct architecture refactoring work package
        
        Args:
            wp_id: Work package identifier
            title: Short title
            modules_affected: List of affected modules
            violation_type: Type of violation (e.g., 'DI', 'GoF', 'SoC')
            
        Returns:
            Complete work package
        """
        return (self.builder
                .set_id(wp_id)
                .set_title(title)
                .set_goal(f"Fix {violation_type} violations in {len(modules_affected)} modules")
                .set_problem(f"{len(modules_affected)} modules failing quality gate due to {violation_type} violations")
                .set_solution(f"Refactor modules to comply with {violation_type} principles")
                .set_priority('HIGH')
                .add_findings([f"Module '{m}' failing {violation_type} checks" for m in modules_affected])
                .add_step(f"Analyze {violation_type} violations in each module")
                .add_step("Design compliant architecture")
                .add_step("Implement refactoring")
                .add_step("Run quality gate verification")
                .add_step("Update documentation")
                .add_benefit("Pass quality gate compliance")
                .add_benefit("Better testability and maintainability")
                .add_benefit("Reduced technical debt")
                .add_reference("docs/knowledge/guidelines/module-quality-gate.md")
                .estimate_effort()
                .build())
    
    def construct_bug_fix(
        self,
        wp_id: str,
        title: str,
        bug_description: str,
        severity: str = 'HIGH'
    ) -> WorkPackage:
        """
        Construct bug fix work package
        
        Args:
            wp_id: Work package identifier
            title: Short title
            bug_description: Detailed bug description
            severity: Bug severity
            
        Returns:
            Complete work package
        """
        return (self.builder
                .set_id(wp_id)
                .set_title(title)
                .set_goal("Fix production bug")
                .set_problem(bug_description)
                .set_solution("Debug, fix root cause, add regression test")
                .set_priority(severity)
                .add_step("Reproduce bug")
                .add_step("Analyze root cause")
                .add_step("Implement fix")
                .add_step("Write regression test")
                .add_step("Verify fix with Gu Wu")
                .add_benefit("Bug eliminated")
                .add_benefit("Regression prevention via tests")
                .estimate_effort()
                .build())
    
    def construct_feature_enhancement(
        self,
        wp_id: str,
        title: str,
        feature_description: str,
        user_value: str
    ) -> WorkPackage:
        """
        Construct feature enhancement work package
        
        Args:
            wp_id: Work package identifier
            title: Short title
            feature_description: What to build
            user_value: Why it matters to users
            
        Returns:
            Complete work package
        """
        return (self.builder
                .set_id(wp_id)
                .set_title(title)
                .set_goal(f"Implement {title}")
                .set_problem(f"Users need: {user_value}")
                .set_solution(feature_description)
                .set_priority('MEDIUM')
                .add_step("Design feature architecture")
                .add_step("Implement backend API")
                .add_step("Write unit tests (100% coverage)")
                .add_step("Implement frontend UI")
                .add_step("Integration testing")
                .add_step("Update documentation")
                .add_benefit(f"User value: {user_value}")
                .add_benefit("Tested and documented")
                .estimate_effort()
                .build())


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_builder_pattern():
    """
    Demonstrate Builder pattern with work package construction
    """
    print("\n" + "="*80)
    print("FENG SHUI BUILDER PATTERN DEMONSTRATION")
    print("="*80 + "\n")
    
    # Example 1: Manual construction with fluent interface
    print("Example 1: Manual Construction (Fluent Interface)")
    print("-" * 80)
    
    builder = WorkPackageBuilder()
    
    wp1 = (builder
           .set_id("WP-FS-001")
           .set_title("Implement GoF Patterns in Feng Shui")
           .set_goal("Transform Feng Shui into modular, extensible architecture engine")
           .set_problem("Hardcoded checks, no extensibility, manual fixes only")
           .set_solution("Apply 5 GoF patterns: Chain, Template, Visitor, Composite, Command")
           .set_priority("HIGH")
           .add_step("Implement Chain of Responsibility (modular checks)")
           .add_step("Implement Template Method (consistent workflow)")
           .add_step("Implement Visitor Pattern (AST analysis)")
           .add_step("Implement Composite Pattern (hierarchical validation)")
           .add_step("Implement Command Pattern (automated fixes)")
           .add_benefit("Modular, extensible architecture")
           .add_benefit("Automated fix capabilities")
           .add_benefit("Consistent workflow across phases")
           .add_reference("docs/knowledge/guidelines/feng-shui-gof-pattern-checks.md")
           .estimate_effort()
           .build())
    
    print(f"\nBuilt: {wp1.wp_id} - {wp1.title}")
    print(f"Estimated Effort: {wp1.effort_hours} hours")
    print(f"Priority: {wp1.priority}")
    print(f"Steps: {len(wp1.implementation_steps)}")
    
    # Example 2: Director-guided construction
    print("\n\nExample 2: Director-Guided Construction (Architecture Refactoring)")
    print("-" * 80)
    
    builder.reset()  # Reuse builder
    director = WorkPackageDirector(builder)
    
    wp2 = director.construct_architecture_refactoring(
        wp_id="WP-DI-001",
        title="Fix DI Violations in Data Products",
        modules_affected=['data_products', 'knowledge_graph', 'api_playground'],
        violation_type='DI'
    )
    
    print(f"\nBuilt: {wp2.wp_id} - {wp2.title}")
    print(f"Estimated Effort: {wp2.effort_hours} hours")
    print(f"Modules: {len(wp2.findings)}")
    
    # Example 3: Bug fix work package
    print("\n\nExample 3: Director-Guided Construction (Bug Fix)")
    print("-" * 80)
    
    builder.reset()
    director = WorkPackageDirector(builder)
    
    wp3 = director.construct_bug_fix(
        wp_id="WP-BUG-001",
        title="Fix Blueprint Registration",
        bug_description="Knowledge Graph API returns 404 - blueprint not registered",
        severity='CRITICAL'
    )
    
    print(f"\nBuilt: {wp3.wp_id} - {wp3.title}")
    print(f"Estimated Effort: {wp3.effort_hours} hours")
    print(f"Priority: {wp3.priority}")
    
    # Example 4: Generate PROJECT_TRACKER.md entry
    print("\n\n" + "="*80)
    print("MARKDOWN GENERATION (for PROJECT_TRACKER.md)")
    print("="*80 + "\n")
    
    print(wp1.format_markdown())
    
    # Summary
    print("\n\n" + "="*80)
    print("BUILDER PATTERN BENEFITS")
    print("="*80)
    print("""
Benefits Demonstrated:
- ✅ Fluent Interface: Readable, chainable method calls
- ✅ Step Validation: Catches missing required fields early
- ✅ Auto Estimation: Calculates effort from complexity
- ✅ Consistent Format: All WPs follow same structure
- ✅ Director Support: Pre-configured for common types
- ✅ Reusable Builder: Reset and build multiple WPs
- ✅ Markdown Export: Ready for PROJECT_TRACKER.md

Construction Methods:
1. Manual: Full control with fluent interface
2. Director: Pre-configured for common patterns
3. Hybrid: Director + manual customization

Next Integration:
- Composite Pattern detects issues → Builder creates WPs automatically
- Command Pattern generates fixes → Builder documents them
- Complete automation loop!
    """)


if __name__ == '__main__':
    demonstrate_builder_pattern()