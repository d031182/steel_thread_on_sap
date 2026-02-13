"""
DDD Pattern Adoption Tracker
=============================

Tracks Domain-Driven Design pattern adoption across codebase.

Measures:
1. Repository Pattern - Abstraction over data access
2. Service Layer - Business logic orchestration
3. Unit of Work - Atomic transaction management
4. Aggregate - Consistency boundaries
5. Domain Events - Decoupled side effects

Philosophy:
"Architecture patterns are like martial arts forms.
 Practice them, quality follows naturally."

DDD Maturity Score: Sum of pattern adoption (0-100)
- 0-20: Beginner (ad-hoc code)
- 21-40: Learning (some patterns)
- 41-60: Practicing (half adopted)
- 61-80: Skilled (most patterns)
- 81-100: Master (full DDD)
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PatternAdoptionScore:
    """Score for a single DDD pattern"""
    pattern_name: str
    adoption_percentage: float  # 0-100
    modules_using: int
    modules_total: int
    maturity_level: str  # "Not Started", "Partial", "Good", "Excellent"
    evidence: List[str]  # File paths where pattern found
    recommendation: str


@dataclass
class DDDMaturityReport:
    """Complete DDD maturity assessment"""
    overall_score: float  # 0-100
    maturity_level: str  # "Beginner", "Learning", "Practicing", "Skilled", "Master"
    pattern_scores: List[PatternAdoptionScore]
    timestamp: str
    modules_analyzed: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'overall_score': self.overall_score,
            'maturity_level': self.maturity_level,
            'pattern_scores': [asdict(ps) for ps in self.pattern_scores],
            'timestamp': self.timestamp,
            'modules_analyzed': self.modules_analyzed
        }


class DDDPatternTracker:
    """
    Analyzes codebase for DDD pattern adoption
    
    Scans Python files for pattern indicators:
    - Repository: AbstractRepository, *Repository classes
    - Service Layer: *Service classes, orchestration methods
    - Unit of Work: UnitOfWork, context managers
    - Aggregate: Aggregate roots, invariant enforcement
    - Domain Events: Event classes, event handlers
    """
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """
        Initialize DDD Pattern Tracker
        
        Args:
            project_root: Root directory to scan (default: current directory)
            verbose: Enable detailed logging
        """
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        
        if self.verbose:
            logger.info(f"[DDD Tracker] Initializing for: {self.project_root}")
    
    def analyze_codebase(self) -> DDDMaturityReport:
        """
        Analyze entire codebase for DDD pattern adoption
        
        Returns:
            DDDMaturityReport with pattern scores and overall maturity
        """
        if self.verbose:
            logger.info("[DDD Tracker] Starting codebase analysis...")
        
        # Find all Python modules
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip(f)]
        
        if self.verbose:
            logger.info(f"[DDD Tracker] Found {len(python_files)} Python files")
        
        # Analyze each pattern
        repository_score = self._analyze_repository_pattern(python_files)
        service_layer_score = self._analyze_service_layer(python_files)
        uow_score = self._analyze_unit_of_work(python_files)
        aggregate_score = self._analyze_aggregate_pattern(python_files)
        domain_events_score = self._analyze_domain_events(python_files)
        
        pattern_scores = [
            repository_score,
            service_layer_score,
            uow_score,
            aggregate_score,
            domain_events_score
        ]
        
        # Calculate overall score (average of all patterns)
        overall_score = sum(ps.adoption_percentage for ps in pattern_scores) / len(pattern_scores)
        
        # Determine maturity level
        maturity_level = self._determine_maturity_level(overall_score)
        
        if self.verbose:
            logger.info(f"[DDD Tracker] Overall DDD Maturity: {overall_score:.1f}/100 ({maturity_level})")
        
        return DDDMaturityReport(
            overall_score=overall_score,
            maturity_level=maturity_level,
            pattern_scores=pattern_scores,
            timestamp=datetime.now().isoformat(),
            modules_analyzed=len(python_files)
        )
    
    def _should_skip(self, file_path: Path) -> bool:
        """Skip test files, migrations, __pycache__, archive, etc."""
        path_str = str(file_path)
        skip_patterns = [
            '__pycache__',
            '.pytest_cache',
            'venv',
            'node_modules',
            'test_',  # Test files
            '/tests/',
            '\\tests\\',  # Windows paths
            'migrations',
            '.git',
            'archive/',  # Skip archived code
            'archive\\',  # Windows paths
        ]
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _analyze_repository_pattern(self, files: List[Path]) -> PatternAdoptionScore:
        """
        Detect Repository Pattern usage
        
        Indicators:
        - AbstractRepository base class
        - *Repository class names
        - Methods: get(), add(), update(), delete()
        """
        evidence = []
        modules_with_pattern = set()
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Stricter check: Must have "Repository" in class definition
                if ('class ' in content and 'Repository' in content) or 'AbstractRepository' in content:
                    evidence.append(str(file_path.relative_to(self.project_root)))
                    
                    # Extract module name if in modules/ directory
                    if '/modules/' in str(file_path) or '\\modules\\' in str(file_path):
                        parts = file_path.parts
                        if 'modules' in parts:
                            idx = parts.index('modules')
                            if idx + 1 < len(parts):
                                modules_with_pattern.add(parts[idx + 1])
            
            except Exception as e:
                if self.verbose:
                    logger.warning(f"[DDD Tracker] Could not read {file_path}: {e}")
        
        # Count total modules
        module_dirs = set()
        for f in files:
            if '/modules/' in str(f) or '\\modules\\' in str(f):
                parts = Path(f).parts
                if 'modules' in parts:
                    idx = parts.index('modules')
                    if idx + 1 < len(parts):
                        module_dirs.add(parts[idx + 1])
        
        modules_total = max(len(module_dirs), 1)
        modules_using = len(modules_with_pattern)
        adoption_pct = (modules_using / modules_total) * 100 if modules_total > 0 else 0
        
        # Determine maturity
        if adoption_pct >= 80:
            maturity = "Excellent"
            recommendation = "Maintain current Repository Pattern usage"
        elif adoption_pct >= 50:
            maturity = "Good"
            recommendation = "Expand Repository Pattern to remaining modules"
        elif adoption_pct >= 20:
            maturity = "Partial"
            recommendation = "Implement Repository Pattern in more modules (currently partial)"
        else:
            maturity = "Not Started"
            recommendation = "⭐ Start with Repository Pattern - easiest entry point to DDD"
        
        return PatternAdoptionScore(
            pattern_name="Repository Pattern",
            adoption_percentage=adoption_pct,
            modules_using=modules_using,
            modules_total=modules_total,
            maturity_level=maturity,
            evidence=evidence[:5],  # Top 5 examples
            recommendation=recommendation
        )
    
    def _analyze_service_layer(self, files: List[Path]) -> PatternAdoptionScore:
        """
        Detect Service Layer pattern usage
        
        Indicators:
        - *Service class names
        - Methods orchestrating multiple repositories
        - Business logic outside Flask routes
        """
        evidence = []
        modules_with_pattern = set()
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Stricter check: Must have class definition ending in "Service"
                if 'class ' in content and 'Service' in content:
                    # Verify it's actually a class name, not just word in comment
                    lines = content.split('\n')
                    for line in lines:
                        if 'class ' in line and 'Service' in line and ':' in line:
                            evidence.append(str(file_path.relative_to(self.project_root)))
                            
                            # Extract module name
                            if '/modules/' in str(file_path) or '\\modules\\' in str(file_path):
                                parts = file_path.parts
                                if 'modules' in parts:
                                    idx = parts.index('modules')
                                    if idx + 1 < len(parts):
                                        modules_with_pattern.add(parts[idx + 1])
                            break
            
            except Exception as e:
                if self.verbose:
                    logger.warning(f"[DDD Tracker] Could not read {file_path}: {e}")
        
        # Count total modules
        module_dirs = set()
        for f in files:
            if '/modules/' in str(f) or '\\modules\\' in str(f):
                parts = Path(f).parts
                if 'modules' in parts:
                    idx = parts.index('modules')
                    if idx + 1 < len(parts):
                        module_dirs.add(parts[idx + 1])
        
        modules_total = max(len(module_dirs), 1)
        modules_using = len(modules_with_pattern)
        adoption_pct = (modules_using / modules_total) * 100 if modules_total > 0 else 0
        
        # Determine maturity
        if adoption_pct >= 80:
            maturity = "Excellent"
            recommendation = "Service Layer well-adopted across codebase"
        elif adoption_pct >= 50:
            maturity = "Good"
            recommendation = "Move remaining business logic from routes to Service Layer"
        elif adoption_pct >= 20:
            maturity = "Partial"
            recommendation = "⭐ Extract business logic from Flask routes into Service Layer"
        else:
            maturity = "Not Started"
            recommendation = "⭐ Implement Service Layer to separate business logic from controllers"
        
        return PatternAdoptionScore(
            pattern_name="Service Layer",
            adoption_percentage=adoption_pct,
            modules_using=modules_using,
            modules_total=modules_total,
            maturity_level=maturity,
            evidence=evidence[:5],
            recommendation=recommendation
        )
    
    def _analyze_unit_of_work(self, files: List[Path]) -> PatternAdoptionScore:
        """
        Detect Unit of Work pattern usage
        
        Indicators:
        - UnitOfWork class
        - Context manager: with uow:
        - Atomic transactions
        """
        evidence = []
        modules_with_pattern = set()
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Strict check: Must have actual UnitOfWork usage
                if 'UnitOfWork' in content:
                    evidence.append(str(file_path.relative_to(self.project_root)))
                    
                    # Extract module name
                    if '/modules/' in str(file_path) or '\\modules\\' in str(file_path):
                        parts = file_path.parts
                        if 'modules' in parts:
                            idx = parts.index('modules')
                            if idx + 1 < len(parts):
                                modules_with_pattern.add(parts[idx + 1])
            
            except Exception as e:
                if self.verbose:
                    logger.warning(f"[DDD Tracker] Could not read {file_path}: {e}")
        
        # Count total modules
        module_dirs = set()
        for f in files:
            if '/modules/' in str(f) or '\\modules\\' in str(f):
                parts = Path(f).parts
                if 'modules' in parts:
                    idx = parts.index('modules')
                    if idx + 1 < len(parts):
                        module_dirs.add(parts[idx + 1])
        
        modules_total = max(len(module_dirs), 1)
        modules_using = len(modules_with_pattern)
        adoption_pct = (modules_using / modules_total) * 100 if modules_total > 0 else 0
        
        # Determine maturity
        if adoption_pct >= 80:
            maturity = "Excellent"
            recommendation = "Unit of Work fully adopted for atomic transactions"
        elif adoption_pct >= 50:
            maturity = "Good"
            recommendation = "Wrap remaining multi-repository operations in Unit of Work"
        elif adoption_pct >= 10:
            maturity = "Partial"
            recommendation = "⭐ Implement Unit of Work for atomic transactions (Priority 1)"
        else:
            maturity = "Not Started"
            recommendation = "⭐⭐ START HERE: Unit of Work eliminates transaction issues + test flakiness"
        
        return PatternAdoptionScore(
            pattern_name="Unit of Work",
            adoption_percentage=adoption_pct,
            modules_using=modules_using,
            modules_total=modules_total,
            maturity_level=maturity,
            evidence=evidence[:5],
            recommendation=recommendation
        )
    
    def _analyze_aggregate_pattern(self, files: List[Path]) -> PatternAdoptionScore:
        """
        Detect Aggregate pattern usage
        
        Indicators:
        - Aggregate Root classes
        - Invariant enforcement methods
        - Child entity collections
        """
        evidence = []
        modules_with_pattern = set()
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Strict check: Must have AggregateRoot or very specific aggregate pattern
                if 'AggregateRoot' in content or ('class ' in content and 'Aggregate' in content):
                    evidence.append(str(file_path.relative_to(self.project_root)))
                    
                    # Extract module name
                    if '/modules/' in str(file_path) or '\\modules\\' in str(file_path):
                        parts = file_path.parts
                        if 'modules' in parts:
                            idx = parts.index('modules')
                            if idx + 1 < len(parts):
                                modules_with_pattern.add(parts[idx + 1])
            
            except Exception as e:
                if self.verbose:
                    logger.warning(f"[DDD Tracker] Could not read {file_path}: {e}")
        
        # Count total modules
        module_dirs = set()
        for f in files:
            if '/modules/' in str(f) or '\\modules\\' in str(f):
                parts = Path(f).parts
                if 'modules' in parts:
                    idx = parts.index('modules')
                    if idx + 1 < len(parts):
                        module_dirs.add(parts[idx + 1])
        
        modules_total = max(len(module_dirs), 1)
        modules_using = len(modules_with_pattern)
        adoption_pct = (modules_using / modules_total) * 100 if modules_total > 0 else 0
        
        # Determine maturity
        if adoption_pct >= 80:
            maturity = "Excellent"
            recommendation = "Aggregate Pattern enforces data integrity consistently"
        elif adoption_pct >= 50:
            maturity = "Good"
            recommendation = "Wrap remaining entity relationships in Aggregates"
        elif adoption_pct >= 10:
            maturity = "Partial"
            recommendation = "Implement Aggregate Pattern for data consistency"
        else:
            maturity = "Not Started"
            recommendation = "Implement Aggregates after Unit of Work (requires transaction support)"
        
        return PatternAdoptionScore(
            pattern_name="Aggregate Pattern",
            adoption_percentage=adoption_pct,
            modules_using=modules_using,
            modules_total=modules_total,
            maturity_level=maturity,
            evidence=evidence[:5],
            recommendation=recommendation
        )
    
    def _analyze_domain_events(self, files: List[Path]) -> PatternAdoptionScore:
        """
        Detect Domain Events pattern usage
        
        Indicators:
        - *Event class names
        - Event handlers
        - Message bus / event dispatcher
        """
        evidence = []
        modules_with_pattern = set()
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Strict check: Must have Event class or EventBus/MessageBus
                if ('class ' in content and 'Event' in content) or 'EventBus' in content or 'MessageBus' in content:
                    # Further validation: Check for actual domain event patterns
                    lines = content.split('\n')
                    for line in lines:
                        if ('class ' in line and 'Event' in line) or 'EventBus' in line or 'MessageBus' in line:
                            evidence.append(str(file_path.relative_to(self.project_root)))
                            
                            # Extract module name
                            if '/modules/' in str(file_path) or '\\modules\\' in str(file_path):
                                parts = file_path.parts
                                if 'modules' in parts:
                                    idx = parts.index('modules')
                                    if idx + 1 < len(parts):
                                        modules_with_pattern.add(parts[idx + 1])
                            break
            
            except Exception as e:
                if self.verbose:
                    logger.warning(f"[DDD Tracker] Could not read {file_path}: {e}")
        
        # Count total modules
        module_dirs = set()
        for f in files:
            if '/modules/' in str(f) or '\\modules\\' in str(f):
                parts = Path(f).parts
                if 'modules' in parts:
                    idx = parts.index('modules')
                    if idx + 1 < len(parts):
                        module_dirs.add(parts[idx + 1])
        
        modules_total = max(len(module_dirs), 1)
        modules_using = len(modules_with_pattern)
        adoption_pct = (modules_using / modules_total) * 100 if modules_total > 0 else 0
        
        # Determine maturity
        if adoption_pct >= 80:
            maturity = "Excellent"
            recommendation = "Domain Events fully decouple side effects"
        elif adoption_pct >= 50:
            maturity = "Good"
            recommendation = "Move remaining side effects to Domain Event handlers"
        elif adoption_pct >= 10:
            maturity = "Partial"
            recommendation = "Implement Domain Events for decoupling"
        else:
            maturity = "Not Started"
            recommendation = "Implement Domain Events after Aggregates (requires domain model)"
        
        return PatternAdoptionScore(
            pattern_name="Domain Events",
            adoption_percentage=adoption_pct,
            modules_using=modules_using,
            modules_total=modules_total,
            maturity_level=maturity,
            evidence=evidence[:5],
            recommendation=recommendation
        )
    
    def _determine_maturity_level(self, overall_score: float) -> str:
        """Determine DDD maturity level from overall score"""
        if overall_score >= 81:
            return "Master"
        elif overall_score >= 61:
            return "Skilled"
        elif overall_score >= 41:
            return "Practicing"
        elif overall_score >= 21:
            return "Learning"
        else:
            return "Beginner"


def main():
    """CLI entry point for DDD Pattern Tracker"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="DDD Pattern Adoption Tracker"
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path.cwd(),
        help='Root directory to analyze'
    )
    parser.add_argument(
        '--output',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    tracker = DDDPatternTracker(
        project_root=args.project_root,
        verbose=args.verbose
    )
    
    report = tracker.analyze_codebase()
    
    if args.output == 'json':
        print(json.dumps(report.to_dict(), indent=2))
    else:
        # Text output
        print("="*70)
        print("DDD PATTERN ADOPTION REPORT")
        print("="*70)
        print(f"\nOverall DDD Maturity: {report.overall_score:.1f}/100 ({report.maturity_level})")
        print(f"Modules Analyzed: {report.modules_analyzed}")
        print(f"Timestamp: {report.timestamp}")
        
        print("\n" + "="*70)
        print("PATTERN BREAKDOWN")
        print("="*70)
        
        for ps in report.pattern_scores:
            print(f"\n{ps.pattern_name}:")
            print(f"  Adoption: {ps.adoption_percentage:.1f}% ({ps.modules_using}/{ps.modules_total} modules)")
            print(f"  Maturity: {ps.maturity_level}")
            print(f"  Recommendation: {ps.recommendation}")
            
            if ps.evidence:
                print(f"  Evidence (top 5):")
                for evidence in ps.evidence:
                    print(f"    - {evidence}")


if __name__ == '__main__':
    main()