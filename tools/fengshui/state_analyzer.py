"""
Architecture State Analyzer for Feng Shui ReAct Agent

Analyzes current architecture state to inform agent decision-making.
Integrates with ModuleQualityGate for comprehensive validation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import json


@dataclass
class ViolationInfo:
    """Information about a specific violation"""
    type: str
    severity: str  # CRITICAL/HIGH/MEDIUM/LOW
    file_path: str
    line_number: int
    description: str
    category: str  # structure/blueprint/di_compliance/interface_usage/coupling


@dataclass
class ArchitectureState:
    """Current state of architecture"""
    feng_shui_score: float  # 0-100
    violations_by_type: Dict[str, List[ViolationInfo]] = field(default_factory=dict)
    violations_by_severity: Dict[str, List[ViolationInfo]] = field(default_factory=dict)
    modules_affected: List[str] = field(default_factory=list)
    recent_fix_history: List[Dict] = field(default_factory=list)
    available_strategies: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    module_scores: Dict[str, float] = field(default_factory=dict)  # Per-module scores
    
    def get_critical_violations(self) -> List[ViolationInfo]:
        """Get all CRITICAL severity violations"""
        return self.violations_by_severity.get('CRITICAL', [])
    
    def get_violations_for_module(self, module_name: str) -> List[ViolationInfo]:
        """Get all violations for a specific module"""
        return [v for violations in self.violations_by_type.values() 
                for v in violations if module_name in v.file_path]


class ArchitectureStateAnalyzer:
    """Analyze current architecture state for decision-making"""
    
    # Severity mapping from quality gate results
    SEVERITY_WEIGHTS = {
        'structure': {'missing_required': 'CRITICAL', 'missing_recommended': 'MEDIUM'},
        'blueprint': {'missing': 'CRITICAL', 'not_exported': 'HIGH'},
        'di_compliance': {'violation': 'CRITICAL'},
        'interface_usage': {'none': 'LOW', 'few': 'MEDIUM'},
        'coupling': {'direct_import': 'MEDIUM'}
    }
    
    def __init__(self, modules_dir: Path = None):
        """
        Initialize state analyzer
        
        Args:
            modules_dir: Path to modules directory (default: ./modules)
        """
        self.modules_dir = modules_dir or Path('modules')
        self.quality_gate = None  # Lazy loaded when needed
        
    def analyze_current_state(self, target_modules: List[str] = None) -> ArchitectureState:
        """
        Comprehensive state analysis
        
        Args:
            target_modules: Specific modules to analyze (None = all modules)
            
        Returns:
            ArchitectureState with complete analysis
        """
        # Import here to avoid circular dependency
        from .module_quality_gate import ModuleQualityGate
        
        if self.quality_gate is None:
            self.quality_gate = ModuleQualityGate()
        
        # Determine modules to analyze
        if target_modules is None:
            target_modules = self._discover_modules()
        
        # Collect violations from all modules
        all_violations = []
        module_scores = {}
        
        for module_name in target_modules:
            module_path = self.modules_dir / module_name
            if not module_path.exists():
                continue
            
            # Run quality gate on module
            result = self.quality_gate.validate(module_path)
            module_scores[module_name] = result.get('overall_score', 0.0) * 100
            
            # Extract violations
            violations = self._extract_violations(module_name, result)
            all_violations.extend(violations)
        
        # Categorize violations
        violations_by_type = self._categorize_by_type(all_violations)
        violations_by_severity = self._categorize_by_severity(all_violations)
        
        # Calculate overall Feng Shui score
        feng_shui_score = self.calculate_feng_shui_score(violations_by_severity)
        
        # Get modules affected
        modules_affected = list(set(v.file_path.split('/')[0] for v in all_violations if '/' in v.file_path))
        
        # Get recent fix history (if reflector available)
        recent_fix_history = self._load_recent_fixes()
        
        # Available strategies
        available_strategies = ['conservative', 'aggressive', 'targeted', 'experimental']
        
        return ArchitectureState(
            feng_shui_score=feng_shui_score,
            violations_by_type=violations_by_type,
            violations_by_severity=violations_by_severity,
            modules_affected=modules_affected,
            recent_fix_history=recent_fix_history,
            available_strategies=available_strategies,
            module_scores=module_scores
        )
    
    def calculate_feng_shui_score(self, violations_by_severity: Dict[str, List[ViolationInfo]]) -> float:
        """
        Calculate overall Feng Shui score (0-100)
        
        Weighting:
        - CRITICAL violations: -20 points each
        - HIGH violations: -10 points each
        - MEDIUM violations: -5 points each
        - LOW violations: -2 points each
        
        Start from 100, deduct points, floor at 0
        
        Args:
            violations_by_severity: Violations grouped by severity
            
        Returns:
            Score from 0.0 to 100.0
        """
        score = 100.0
        
        # Deduct points based on severity
        score -= len(violations_by_severity.get('CRITICAL', [])) * 20
        score -= len(violations_by_severity.get('HIGH', [])) * 10
        score -= len(violations_by_severity.get('MEDIUM', [])) * 5
        score -= len(violations_by_severity.get('LOW', [])) * 2
        
        # Floor at 0
        return max(0.0, score)
    
    def categorize_violations(self, raw_violations: List[Dict]) -> Dict[str, List[ViolationInfo]]:
        """
        Group violations by type for targeted fixing
        
        Args:
            raw_violations: Raw violation data from quality gate
            
        Returns:
            Dict mapping violation type to list of ViolationInfo objects
        """
        categorized = {}
        
        for v in raw_violations:
            violation_type = v.get('type', 'unknown')
            if violation_type not in categorized:
                categorized[violation_type] = []
            
            categorized[violation_type].append(ViolationInfo(
                type=violation_type,
                severity=v.get('severity', 'MEDIUM'),
                file_path=v.get('file_path', ''),
                line_number=v.get('line_number', 0),
                description=v.get('description', ''),
                category=v.get('category', 'unknown')
            ))
        
        return categorized
    
    def identify_critical_path(self, violations: Dict[str, List[ViolationInfo]]) -> List[str]:
        """
        Identify which violations to fix first (critical path)
        
        Priority order:
        1. CRITICAL violations (blocking deployment)
        2. HIGH violations (major issues)
        3. MEDIUM violations (technical debt)
        4. LOW violations (nice to have)
        
        Args:
            violations: Violations grouped by type
            
        Returns:
            Ordered list of violation types to fix
        """
        # Flatten all violations
        all_violations = [v for violations_list in violations.values() for v in violations_list]
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_violations = sorted(all_violations, key=lambda v: severity_order.get(v.severity, 4))
        
        # Get unique types in priority order
        critical_path = []
        seen_types = set()
        
        for v in sorted_violations:
            if v.type not in seen_types:
                critical_path.append(v.type)
                seen_types.add(v.type)
        
        return critical_path
    
    def _discover_modules(self) -> List[str]:
        """Discover all modules in modules directory"""
        if not self.modules_dir.exists():
            return []
        
        modules = []
        for path in self.modules_dir.iterdir():
            if path.is_dir() and not path.name.startswith('_'):
                # Check if it has module.json
                if (path / 'module.json').exists():
                    modules.append(path.name)
        
        return modules
    
    def _extract_violations(self, module_name: str, quality_gate_result: Dict) -> List[ViolationInfo]:
        """Extract violations from quality gate result"""
        violations = []
        
        if not quality_gate_result.get('passed', True):
            results = quality_gate_result.get('results', {})
            
            for category, result in results.items():
                # Extract issues
                for issue in result.issues:
                    violations.append(ViolationInfo(
                        type=category,
                        severity='CRITICAL' if 'CRITICAL' in issue else 'HIGH',
                        file_path=f"{module_name}/{category}",
                        line_number=0,
                        description=issue,
                        category=category
                    ))
                
                # Extract warnings as lower severity
                for warning in result.warnings:
                    violations.append(ViolationInfo(
                        type=category,
                        severity='MEDIUM' if 'RECOMMENDED' in warning else 'LOW',
                        file_path=f"{module_name}/{category}",
                        line_number=0,
                        description=warning,
                        category=category
                    ))
        
        return violations
    
    def _categorize_by_type(self, violations: List[ViolationInfo]) -> Dict[str, List[ViolationInfo]]:
        """Group violations by type"""
        by_type = {}
        
        for v in violations:
            if v.type not in by_type:
                by_type[v.type] = []
            by_type[v.type].append(v)
        
        return by_type
    
    def _categorize_by_severity(self, violations: List[ViolationInfo]) -> Dict[str, List[ViolationInfo]]:
        """Group violations by severity"""
        by_severity = {}
        
        for v in violations:
            if v.severity not in by_severity:
                by_severity[v.severity] = []
            by_severity[v.severity].append(v)
        
        return by_severity
    
    def _load_recent_fixes(self, limit: int = 10) -> List[Dict]:
        """
        Load recent fix history from reflector database
        
        Args:
            limit: Maximum number of recent fixes to load
            
        Returns:
            List of recent fix attempts
        """
        try:
            # Try to load from reflector if available
            reflection_db = Path(__file__).parent / 'reflection.db'
            if reflection_db.exists():
                import sqlite3
                conn = sqlite3.connect(reflection_db)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT timestamp, fix_type, module_name, strategy_used, actual_success
                    FROM fix_attempts
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                conn.close()
                
                return [
                    {
                        'timestamp': row[0],
                        'fix_type': row[1],
                        'module_name': row[2],
                        'strategy': row[3],
                        'success': bool(row[4])
                    }
                    for row in rows
                ]
        except Exception:
            pass
        
        return []