#!/usr/bin/env python3
"""
Feng Shui Architecture History - Memento Pattern
=================================================

Track architecture evolution with rollback capabilities.

GoF Pattern: Memento
- Captures architecture state snapshots
- Enables rollback to previous states
- Tracks improvement progress over time
- Proves ROI with historical comparisons
"""
import sys
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add UTF-8 reconfiguration for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class ArchitectureSnapshot:
    """
    Memento: Captures complete architecture state at a point in time
    
    Stores:
    - Quality metrics (score, issues)
    - Module compliance status
    - Performance metrics
    - Git commit reference
    """
    timestamp: str
    git_commit: str
    feng_shui_score: int
    grade: str
    total_modules: int
    passing_modules: int
    total_issues: int
    critical_issues: int
    high_issues: int
    module_scores: Dict[str, int]  # module_name → score
    metadata: Dict[str, Any]  # Additional context
    
    def compare_with(self, other: 'ArchitectureSnapshot') -> 'ArchitectureComparison':
        """
        Compare this snapshot with another
        
        Args:
            other: Snapshot to compare against
            
        Returns:
            ArchitectureComparison showing differences
        """
        return ArchitectureComparison(self, other)


@dataclass
class ArchitectureComparison:
    """
    Comparison between two architecture snapshots
    
    Shows:
    - Score changes
    - Issue resolution progress
    - Module improvements
    - Time elapsed
    """
    before: ArchitectureSnapshot
    after: ArchitectureSnapshot
    
    @property
    def score_delta(self) -> int:
        """Change in feng shui score"""
        return self.after.feng_shui_score - self.before.feng_shui_score
    
    @property
    def grade_improved(self) -> bool:
        """Whether grade improved"""
        grades = ['F', 'D', 'C', 'B', 'A', 'S']
        before_idx = grades.index(self.before.grade)
        after_idx = grades.index(self.after.grade)
        return after_idx > before_idx
    
    @property
    def issues_resolved(self) -> int:
        """Number of issues resolved"""
        return self.before.total_issues - self.after.total_issues
    
    @property
    def critical_resolved(self) -> int:
        """Number of critical issues resolved"""
        return self.before.critical_issues - self.after.critical_issues
    
    @property
    def modules_improved(self) -> List[str]:
        """List of modules with improved scores"""
        improved = []
        for module in self.before.module_scores:
            if module in self.after.module_scores:
                if self.after.module_scores[module] > self.before.module_scores[module]:
                    improved.append(module)
        return improved
    
    def print_summary(self):
        """Print comparison summary"""
        print("\n" + "="*80)
        print("ARCHITECTURE EVOLUTION COMPARISON")
        print("="*80)
        
        # Time period
        before_time = datetime.fromisoformat(self.before.timestamp)
        after_time = datetime.fromisoformat(self.after.timestamp)
        elapsed = after_time - before_time
        
        print(f"\nTime Period: {before_time.strftime('%Y-%m-%d %H:%M')} → {after_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Duration: {elapsed.days} days, {elapsed.seconds // 3600} hours")
        
        # Overall score
        print(f"\nFeng Shui Score: {self.before.feng_shui_score} → {self.after.feng_shui_score} ", end="")
        if self.score_delta > 0:
            print(f"(+{self.score_delta} [IMPROVED])")
        elif self.score_delta < 0:
            print(f"({self.score_delta} [REGRESSED])")
        else:
            print("(unchanged)")
        
        # Grade
        print(f"Grade: {self.before.grade} → {self.after.grade} ", end="")
        if self.grade_improved:
            print("[IMPROVED]")
        else:
            print()
        
        # Issues
        print(f"\nIssues Resolved: {self.issues_resolved}")
        print(f"  Critical: {self.before.critical_issues} → {self.after.critical_issues} ({self.critical_resolved} resolved)")
        print(f"  High: {self.before.high_issues} → {self.after.high_issues} ({self.before.high_issues - self.after.high_issues} resolved)")
        
        # Modules
        print(f"\nModule Compliance: {self.before.passing_modules}/{self.before.total_modules} → {self.after.passing_modules}/{self.after.total_modules}")
        
        if self.modules_improved:
            print(f"\nImproved Modules ({len(self.modules_improved)}):")
            for module in self.modules_improved:
                before_score = self.before.module_scores[module]
                after_score = self.after.module_scores[module]
                delta = after_score - before_score
                print(f"  - {module}: {before_score} → {after_score} (+{delta})")


class ArchitectureCaretaker:
    """
    Caretaker: Manages architecture snapshots (Memento pattern)
    
    Responsibilities:
    - Save snapshots to persistent storage
    - Retrieve snapshots by date/commit
    - Compare snapshots for evolution tracking
    - Provide rollback capabilities
    """
    
    def __init__(self, db_path: str = "tools/fengshui/architecture_history.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Create database schema if not exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                git_commit TEXT NOT NULL,
                feng_shui_score INTEGER NOT NULL,
                grade TEXT NOT NULL,
                total_modules INTEGER NOT NULL,
                passing_modules INTEGER NOT NULL,
                total_issues INTEGER NOT NULL,
                critical_issues INTEGER NOT NULL,
                high_issues INTEGER NOT NULL,
                module_scores TEXT NOT NULL,  -- JSON
                metadata TEXT NOT NULL,        -- JSON
                UNIQUE(git_commit)
            )
        """)
        
        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp 
            ON snapshots(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def save_snapshot(self, snapshot: ArchitectureSnapshot) -> bool:
        """
        Save architecture snapshot
        
        Args:
            snapshot: Snapshot to save
            
        Returns:
            True if saved successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO snapshots (
                    timestamp, git_commit, feng_shui_score, grade,
                    total_modules, passing_modules, total_issues,
                    critical_issues, high_issues, module_scores, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.timestamp,
                snapshot.git_commit,
                snapshot.feng_shui_score,
                snapshot.grade,
                snapshot.total_modules,
                snapshot.passing_modules,
                snapshot.total_issues,
                snapshot.critical_issues,
                snapshot.high_issues,
                json.dumps(snapshot.module_scores),
                json.dumps(snapshot.metadata)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_snapshot(self, git_commit: str) -> Optional[ArchitectureSnapshot]:
        """
        Retrieve snapshot by git commit
        
        Args:
            git_commit: Git commit hash
            
        Returns:
            ArchitectureSnapshot or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, git_commit, feng_shui_score, grade,
                   total_modules, passing_modules, total_issues,
                   critical_issues, high_issues, module_scores, metadata
            FROM snapshots
            WHERE git_commit = ?
        """, (git_commit,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ArchitectureSnapshot(
            timestamp=row[0],
            git_commit=row[1],
            feng_shui_score=row[2],
            grade=row[3],
            total_modules=row[4],
            passing_modules=row[5],
            total_issues=row[6],
            critical_issues=row[7],
            high_issues=row[8],
            module_scores=json.loads(row[9]),
            metadata=json.loads(row[10])
        )
    
    def get_latest_snapshot(self) -> Optional[ArchitectureSnapshot]:
        """Get most recent snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, git_commit, feng_shui_score, grade,
                   total_modules, passing_modules, total_issues,
                   critical_issues, high_issues, module_scores, metadata
            FROM snapshots
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return ArchitectureSnapshot(
            timestamp=row[0],
            git_commit=row[1],
            feng_shui_score=row[2],
            grade=row[3],
            total_modules=row[4],
            passing_modules=row[5],
            total_issues=row[6],
            critical_issues=row[7],
            high_issues=row[8],
            module_scores=json.loads(row[9]),
            metadata=json.loads(row[10])
        )
    
    def get_all_snapshots(self) -> List[ArchitectureSnapshot]:
        """Get all snapshots ordered by timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, git_commit, feng_shui_score, grade,
                   total_modules, passing_modules, total_issues,
                   critical_issues, high_issues, module_scores, metadata
            FROM snapshots
            ORDER BY timestamp ASC
        """)
        
        snapshots = []
        for row in cursor.fetchall():
            snapshots.append(ArchitectureSnapshot(
                timestamp=row[0],
                git_commit=row[1],
                feng_shui_score=row[2],
                grade=row[3],
                total_modules=row[4],
                passing_modules=row[5],
                total_issues=row[6],
                critical_issues=row[7],
                high_issues=row[8],
                module_scores=json.loads(row[9]),
                metadata=json.loads(row[10])
            ))
        
        conn.close()
        return snapshots
    
    def compare_last_two(self) -> Optional[ArchitectureComparison]:
        """Compare the two most recent snapshots"""
        snapshots = self.get_all_snapshots()
        
        if len(snapshots) < 2:
            return None
        
        return ArchitectureComparison(snapshots[-2], snapshots[-1])
    
    def get_evolution_trend(self) -> Dict[str, Any]:
        """
        Calculate evolution trends across all snapshots
        
        Returns:
            Dict with trend statistics
        """
        snapshots = self.get_all_snapshots()
        
        if not snapshots:
            return {'error': 'No snapshots available'}
        
        scores = [s.feng_shui_score for s in snapshots]
        issues = [s.total_issues for s in snapshots]
        
        return {
            'total_snapshots': len(snapshots),
            'first_score': scores[0],
            'latest_score': scores[-1],
            'score_improvement': scores[-1] - scores[0],
            'peak_score': max(scores),
            'lowest_score': min(scores),
            'issues_resolved': issues[0] - issues[-1] if len(issues) > 1 else 0,
            'average_score': sum(scores) // len(scores),
            'trend': 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable'
        }


class ArchitectureOriginator:
    """
    Originator: Creates and restores architecture snapshots
    
    Responsibilities:
    - Capture current architecture state
    - Restore to previous state (rollback)
    - Work with Caretaker for persistence
    """
    
    def __init__(self):
        self.current_state: Optional[ArchitectureSnapshot] = None
    
    def capture_snapshot(self) -> ArchitectureSnapshot:
        """
        Capture current architecture state
        
        Returns:
            ArchitectureSnapshot of current state
        """
        # Get git commit
        import subprocess
        try:
            git_commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                text=True
            ).strip()
        except:
            git_commit = 'unknown'
        
        # Get feng shui score (would integrate with quality_check.py)
        # For demo, using mock data
        snapshot = ArchitectureSnapshot(
            timestamp=datetime.now().isoformat(),
            git_commit=git_commit,
            feng_shui_score=93,
            grade='A',
            total_modules=10,
            passing_modules=8,
            total_issues=44,
            critical_issues=2,
            high_issues=17,
            module_scores={
                'knowledge_graph': 93,
                'data_products': 85,
                'api_playground': 80,
                'hana_connection': 75,
                'log_manager': 88,
                'login_manager': 95,
                'feature_manager': 82,
                'sql_execution': 78,
                'sqlite_connection': 90,
                'csn_validation': 70
            },
            metadata={
                'phase': '4.8',
                'work_package': 'WP-FS-001',
                'notes': 'After GoF pattern implementation'
            }
        )
        
        self.current_state = snapshot
        return snapshot
    
    def restore_snapshot(self, snapshot: ArchitectureSnapshot):
        """
        Restore to a previous architecture state
        
        Args:
            snapshot: Snapshot to restore to
            
        Note:
            In practice, this would:
            1. Git checkout to snapshot.git_commit
            2. Verify architecture matches snapshot
            3. Update current_state
        """
        self.current_state = snapshot
        print(f"\nRestored to snapshot: {snapshot.timestamp}")
        print(f"Git commit: {snapshot.git_commit}")
        print(f"Score: {snapshot.feng_shui_score} (Grade {snapshot.grade})")


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_memento_pattern():
    """
    Demonstrate Memento pattern with architecture history
    """
    print("\n" + "="*80)
    print("FENG SHUI MEMENTO PATTERN DEMONSTRATION")
    print("="*80 + "\n")
    
    # Create components
    originator = ArchitectureOriginator()
    caretaker = ArchitectureCaretaker()
    
    # Capture current state
    print("Capturing current architecture state...")
    current = originator.capture_snapshot()
    caretaker.save_snapshot(current)
    print(f"  [SAVED] Score: {current.feng_shui_score}, Grade: {current.grade}")
    print(f"  Issues: {current.total_issues} total ({current.critical_issues} critical, {current.high_issues} high)")
    
    # Simulate improvement (Phase 4.9 complete)
    print("\nSimulating architecture improvement (Phase 4.9)...")
    improved = ArchitectureSnapshot(
        timestamp=datetime.now().isoformat(),
        git_commit='phase4.9_complete',
        feng_shui_score=96,
        grade='A',
        total_modules=10,
        passing_modules=10,  # All passing now!
        total_issues=15,     # Reduced from 44
        critical_issues=0,   # All resolved!
        high_issues=5,       # Reduced from 17
        module_scores={
            'knowledge_graph': 96,
            'data_products': 92,
            'api_playground': 88,
            'hana_connection': 90,
            'log_manager': 93,
            'login_manager': 95,
            'feature_manager': 90,
            'sql_execution': 91,
            'sqlite_connection': 94,
            'csn_validation': 85
        },
        metadata={
            'phase': '4.9',
            'work_package': 'COMPLETE',
            'notes': 'All GoF patterns implemented'
        }
    )
    caretaker.save_snapshot(improved)
    print(f"  [SAVED] Score: {improved.feng_shui_score}, Grade: {improved.grade}")
    
    # Compare evolution
    print("\n" + "="*80)
    print("EVOLUTION ANALYSIS")
    print("="*80)
    
    comparison = current.compare_with(improved)
    comparison.print_summary()
    
    # Evolution trends
    print("\n" + "="*80)
    print("EVOLUTION TRENDS")
    print("="*80)
    trend = caretaker.get_evolution_trend()
    print(f"\nTotal Snapshots: {trend['total_snapshots']}")
    print(f"Score Trajectory: {trend['first_score']} → {trend['latest_score']} ({trend['trend']})")
    print(f"Total Improvement: +{trend['score_improvement']} points")
    print(f"Issues Resolved: {trend['issues_resolved']}")
    
    # Demonstrate rollback capability
    print("\n" + "="*80)
    print("ROLLBACK DEMONSTRATION (commented out - uncomment to test)")
    print("="*80)
    print("  # Rollback to previous state:")
    print(f"  # originator.restore_snapshot(current)")
    print(f"  # git checkout {current.git_commit}")
    print("  # Result: Architecture reverted, can re-apply improvements")


if __name__ == '__main__':
    demonstrate_memento_pattern()