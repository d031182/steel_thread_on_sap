"""
Feng Shui Interface: Shi Fu's Connection to the Architecture Disciple
=====================================================================

Reads Feng Shui's databases and reports to understand code quality patterns.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


@dataclass
class ViolationSummary:
    """Summary of violations from Feng Shui"""
    total_violations: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    violations_by_type: Dict[str, int]
    violations_by_module: Dict[str, int]
    recent_violations: List[Dict]


class FengShuiInterface:
    """
    Interface to Feng Shui (风水) - The Architecture Disciple
    
    Reads from Feng Shui's violation database and multi-agent reports
    to understand code quality patterns.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize Feng Shui interface
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.db_path = project_root / "tools" / "fengshui" / "feng_shui.db"
        
        if not self.db_path.exists():
            logger.warning(f"[Feng Shui Interface] Database not found: {self.db_path}")
    
    def get_recent_violations(self, days: int = 7) -> List[Dict]:
        """
        Get violations from last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of violation dictionaries
        """
        if not self.db_path.exists():
            logger.warning("[Feng Shui Interface] No database, returning empty list")
            return []
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    violation_id,
                    module_name,
                    file_path,
                    violation_type,
                    severity,
                    description,
                    recommendation,
                    detected_at,
                    agent_name
                FROM violations
                WHERE detected_at >= ?
                ORDER BY detected_at DESC
            """, (cutoff_date,))
            
            violations = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            logger.info(f"[Feng Shui Interface] Retrieved {len(violations)} violations from last {days} days")
            return violations
            
        except sqlite3.Error as e:
            logger.error(f"[Feng Shui Interface] Database error: {e}")
            return []
    
    def get_violation_summary(self, days: int = 7) -> ViolationSummary:
        """
        Get summary statistics of violations
        
        Args:
            days: Number of days to look back
        
        Returns:
            ViolationSummary object
        """
        violations = self.get_recent_violations(days)
        
        if not violations:
            return ViolationSummary(
                total_violations=0,
                critical_count=0,
                high_count=0,
                medium_count=0,
                low_count=0,
                violations_by_type={},
                violations_by_module={},
                recent_violations=[]
            )
        
        # Count by severity
        severity_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for v in violations:
            severity = v.get('severity', 'LOW').upper()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Count by type
        by_type = {}
        for v in violations:
            vtype = v.get('violation_type', 'UNKNOWN')
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        # Count by module
        by_module = {}
        for v in violations:
            module = v.get('module_name', 'unknown')
            by_module[module] = by_module.get(module, 0) + 1
        
        return ViolationSummary(
            total_violations=len(violations),
            critical_count=severity_counts['CRITICAL'],
            high_count=severity_counts['HIGH'],
            medium_count=severity_counts['MEDIUM'],
            low_count=severity_counts['LOW'],
            violations_by_type=by_type,
            violations_by_module=by_module,
            recent_violations=violations[:20]  # Top 20 most recent
        )
    
    def get_overall_score(self) -> float:
        """
        Get overall Feng Shui quality score
        
        Returns:
            Score from 0-100
        """
        if not self.db_path.exists():
            logger.warning("[Feng Shui Interface] No database, returning default score")
            return 85.0  # Default optimistic score
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get most recent module scores
            cursor.execute("""
                SELECT AVG(health_score) as avg_score
                FROM module_health
                WHERE scan_date >= date('now', '-7 days')
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] is not None:
                return float(result[0])
            
            # Fallback: Calculate from violations
            summary = self.get_violation_summary(days=7)
            
            if summary.total_violations == 0:
                return 100.0
            
            # Simple scoring: Start at 100, deduct for violations
            score = 100.0
            score -= summary.critical_count * 5.0  # -5 per critical
            score -= summary.high_count * 2.0      # -2 per high
            score -= summary.medium_count * 0.5    # -0.5 per medium
            score -= summary.low_count * 0.1       # -0.1 per low
            
            return max(0.0, score)
            
        except sqlite3.Error as e:
            logger.error(f"[Feng Shui Interface] Database error: {e}")
            return 85.0  # Default fallback
    
    def get_modules_with_issues(self, min_violations: int = 5) -> List[str]:
        """
        Get modules with significant violation counts
        
        Args:
            min_violations: Minimum violations to be considered
        
        Returns:
            List of module names
        """
        summary = self.get_violation_summary(days=7)
        
        return [
            module for module, count in summary.violations_by_module.items()
            if count >= min_violations
        ]
    
    def get_violations_by_type(self, violation_type: str, days: int = 7) -> List[Dict]:
        """
        Get all violations of a specific type
        
        Args:
            violation_type: Type to filter (e.g., 'DI_VIOLATION', 'SECURITY_ISSUE')
            days: Number of days to look back
        
        Returns:
            List of matching violations
        """
        all_violations = self.get_recent_violations(days)
        
        return [
            v for v in all_violations
            if v.get('violation_type', '').upper() == violation_type.upper()
        ]