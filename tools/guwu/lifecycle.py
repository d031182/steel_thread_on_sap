"""
Gu Wu Test Lifecycle Manager - Stage 4 of Phase 3

Autonomously manages test creation, retirement, and maintenance.
Monitors codebase changes and automatically maintains test quality.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import ast
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class LifecycleAction(Enum):
    """Types of lifecycle actions"""
    CREATE = "create"           # Create new test
    RETIRE = "retire"           # Remove obsolete test
    REFACTOR = "refactor"       # Improve existing test
    UPDATE = "update"           # Update test after code change


@dataclass
class LifecycleRecommendation:
    """A recommended lifecycle action"""
    action: LifecycleAction
    target: str                 # Test or code file
    reason: str                 # Why this action is needed
    priority: str               # low/medium/high/critical
    details: Dict               # Action-specific details
    automated: bool             # Can be automated?
    script: Optional[str]       # Automation script (if automated)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'action': self.action.value,
            'target': self.target,
            'reason': self.reason,
            'priority': self.priority,
            'details': self.details,
            'automated': self.automated,
            'script': self.script
        }


class TestLifecycleManager:
    """
    Autonomous test lifecycle management.
    
    Responsibilities:
    1. Auto-create tests for new code
    2. Auto-retire tests for deleted code
    3. Auto-refactor slow/flaky tests
    4. Auto-update tests after code changes
    """
    
    def __init__(self, project_root: str = ".", db_path: str = "tools/guwu/metrics.db"):
        self.project_root = Path(project_root)
        self.db_path = Path(db_path)
        
        # Initialize lifecycle database
        self._init_lifecycle_db()
    
    def _init_lifecycle_db(self):
        """Initialize lifecycle tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Track lifecycle actions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lifecycle_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                target TEXT NOT NULL,
                reason TEXT NOT NULL,
                automated BOOLEAN NOT NULL,
                executed BOOLEAN DEFAULT 0,
                timestamp TEXT NOT NULL,
                result TEXT
            )
        ''')
        
        # Track code-test mapping
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_test_mapping (
                code_file TEXT NOT NULL,
                test_file TEXT NOT NULL,
                last_synced TEXT NOT NULL,
                PRIMARY KEY (code_file, test_file)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_lifecycle(self) -> List[LifecycleRecommendation]:
        """
        Analyze entire project for lifecycle needs.
        
        Returns: List of recommended actions sorted by priority
        """
        recommendations = []
        
        # 1. Find new code needing tests (CREATE)
        create_actions = self._find_new_code_needing_tests()
        recommendations.extend(create_actions)
        
        # 2. Find obsolete tests (RETIRE)
        retire_actions = self._find_obsolete_tests()
        recommendations.extend(retire_actions)
        
        # 3. Find tests needing refactoring (REFACTOR)
        refactor_actions = self._find_tests_needing_refactoring()
        recommendations.extend(refactor_actions)
        
        # 4. Find tests needing updates (UPDATE)
        update_actions = self._find_tests_needing_updates()
        recommendations.extend(update_actions)
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))
        
        return recommendations
    
    def _find_new_code_needing_tests(self) -> List[LifecycleRecommendation]:
        """Find recently added code that needs tests"""
        recommendations = []
        
        try:
            # Get files added in last 7 days
            result = subprocess.run(
                ['git', 'diff', '--name-status', 'HEAD~7..HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                status = parts[0]
                file_path = parts[1]
                
                # Only process added Python files in modules/core
                if status != 'A' or not file_path.endswith('.py'):
                    continue
                
                if not (file_path.startswith('modules/') or file_path.startswith('core/')):
                    continue
                
                if 'test_' in file_path:
                    continue
                
                # Check if test exists
                test_file = self._get_test_file_path(Path(file_path))
                
                if not test_file.exists():
                    # Generate test template
                    template = self._generate_test_template(Path(file_path))
                    
                    recommendations.append(LifecycleRecommendation(
                        action=LifecycleAction.CREATE,
                        target=str(test_file),
                        reason=f"New file added without tests: {file_path}",
                        priority='high',
                        details={
                            'source_file': file_path,
                            'template': template
                        },
                        automated=True,
                        script=self._generate_create_script(test_file, template)
                    ))
        
        except subprocess.CalledProcessError:
            pass
        
        return recommendations
    
    def _find_obsolete_tests(self) -> List[LifecycleRecommendation]:
        """Find tests for deleted/moved code"""
        recommendations = []
        
        # Get all test files
        for test_file in self.project_root.rglob('test_*.py'):
            if 'tests/' not in str(test_file):
                continue
            
            # Find corresponding source file
            source_file = self._get_source_file_path(test_file)
            
            if not source_file.exists():
                # Source file doesn't exist - test is obsolete
                recommendations.append(LifecycleRecommendation(
                    action=LifecycleAction.RETIRE,
                    target=str(test_file),
                    reason=f"Source file no longer exists: {source_file}",
                    priority='medium',
                    details={
                        'missing_source': str(source_file),
                        'can_delete': True
                    },
                    automated=True,
                    script=self._generate_retire_script(test_file)
                ))
        
        return recommendations
    
    def _find_tests_needing_refactoring(self) -> List[LifecycleRecommendation]:
        """Find slow or flaky tests that need refactoring"""
        recommendations = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find slow tests (> 5 seconds average)
        cursor.execute('''
            SELECT test_id, test_name, avg_duration, total_runs
            FROM test_statistics
            WHERE avg_duration > 5.0
            ORDER BY avg_duration DESC
            LIMIT 10
        ''')
        
        for row in cursor.fetchall():
            test_id, test_name, avg_duration, total_runs = row
            
            recommendations.append(LifecycleRecommendation(
                action=LifecycleAction.REFACTOR,
                target=test_id,
                reason=f"Slow test: {avg_duration:.1f}s average duration",
                priority='medium',
                details={
                    'avg_duration': avg_duration,
                    'total_runs': total_runs,
                    'suggestions': [
                        'Use mocks for external dependencies',
                        'Reduce test data size',
                        'Move to integration test layer',
                        'Use fixtures for expensive setup'
                    ]
                },
                automated=False,  # Requires human judgment
                script=None
            ))
        
        # Find flaky tests (flaky_score > 0.5)
        cursor.execute('''
            SELECT test_id, test_name, flaky_score, total_runs
            FROM test_statistics
            WHERE flaky_score > 0.5
            ORDER BY flaky_score DESC
            LIMIT 10
        ''')
        
        for row in cursor.fetchall():
            test_id, test_name, flaky_score, total_runs = row
            
            recommendations.append(LifecycleRecommendation(
                action=LifecycleAction.REFACTOR,
                target=test_id,
                reason=f"Flaky test: {flaky_score:.1%} failure rate",
                priority='high',
                details={
                    'flaky_score': flaky_score,
                    'total_runs': total_runs,
                    'suggestions': [
                        'Add explicit waits/timeouts',
                        'Remove race conditions',
                        'Fix timing dependencies',
                        'Add retry logic if appropriate'
                    ]
                },
                automated=False,  # Requires debugging
                script=None
            ))
        
        conn.close()
        return recommendations
    
    def _find_tests_needing_updates(self) -> List[LifecycleRecommendation]:
        """Find tests that are out of sync with code changes"""
        recommendations = []
        
        try:
            # Get files changed in last 7 days
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~7..HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = set(result.stdout.strip().split('\n'))
            changed_files = {f for f in changed_files if f.endswith('.py') and f}
            
            for file_path in changed_files:
                if 'test_' in file_path:
                    continue
                
                # Check if corresponding test was also updated
                full_path = self.project_root / file_path
                if not full_path.exists():
                    continue
                
                test_file = self._get_test_file_path(full_path)
                test_file_relative = str(test_file.relative_to(self.project_root))
                
                if test_file_relative not in changed_files:
                    # Code changed but test didn't - needs review
                    recommendations.append(LifecycleRecommendation(
                        action=LifecycleAction.UPDATE,
                        target=str(test_file),
                        reason=f"Code changed but test not updated: {file_path}",
                        priority='high',
                        details={
                            'source_file': file_path,
                            'test_exists': test_file.exists(),
                            'action_needed': 'Review test coverage for recent changes'
                        },
                        automated=False,  # Requires understanding changes
                        script=None
                    ))
        
        except subprocess.CalledProcessError:
            pass
        
        return recommendations
    
    def _get_test_file_path(self, source_file: Path) -> Path:
        """Get test file path for a source file"""
        relative = source_file.relative_to(self.project_root)
        parts = list(relative.parts)
        
        # Remove backend/services subdirectory
        if 'backend' in parts:
            parts.remove('backend')
        
        # Add test_ prefix to filename
        filename = f"test_{parts[-1]}"
        parts[-1] = filename
        
        # Build test path
        test_path = self.project_root / 'tests' / 'unit' / Path(*parts)
        return test_path
    
    def _get_source_file_path(self, test_file: Path) -> Path:
        """Get source file path from test file"""
        relative = test_file.relative_to(self.project_root)
        parts = list(relative.parts)
        
        # Remove 'tests' and 'unit'
        if 'tests' in parts:
            parts.remove('tests')
        if 'unit' in parts:
            parts.remove('unit')
        
        # Remove test_ prefix
        filename = parts[-1].replace('test_', '')
        parts[-1] = filename
        
        # Add backend if it's a module
        if len(parts) >= 2 and parts[0] == 'modules':
            parts.insert(2, 'backend')
        
        return self.project_root / Path(*parts)
    
    def _generate_test_template(self, source_file: Path) -> str:
        """Generate test template for a source file"""
        module_name = self._file_to_module(source_file)
        
        template = f'''"""
Tests for {module_name}

Auto-generated by Gu Wu Lifecycle Manager
"""

import pytest

@pytest.mark.unit
@pytest.mark.fast
def test_{module_name.split('.')[-1]}_placeholder():
    """
    Placeholder test for {module_name}.
    
    TODO: Replace with actual tests after reviewing {source_file.name}
    """
    # ARRANGE
    # TODO: Set up test data
    
    # ACT
    # TODO: Call function to test
    
    # ASSERT
    # TODO: Verify results
    pass
'''
        return template.strip()
    
    def _file_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        relative = file_path.relative_to(self.project_root)
        parts = list(relative.parts)
        
        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        
        # Remove backend subdirectory for module name
        if 'backend' in parts:
            parts.remove('backend')
        
        return '.'.join(parts[:2]) if len(parts) >= 2 else '.'.join(parts)
    
    def _generate_create_script(self, test_file: Path, template: str) -> str:
        """Generate script to create new test file"""
        script = f'''
# Auto-create test file: {test_file}
import os
from pathlib import Path

test_file = Path(r"{test_file}")
test_file.parent.mkdir(parents=True, exist_ok=True)

template = """{template}"""

test_file.write_text(template, encoding='utf-8')
print(f"✓ Created: {{test_file}}")
'''
        return script.strip()
    
    def _generate_retire_script(self, test_file: Path) -> str:
        """Generate script to retire obsolete test file"""
        script = f'''
# Auto-retire obsolete test: {test_file}
import os
from pathlib import Path

test_file = Path(r"{test_file}")

if test_file.exists():
    # Move to archive instead of deleting
    archive_dir = test_file.parent / 'archived'
    archive_dir.mkdir(exist_ok=True)
    
    archive_path = archive_dir / test_file.name
    test_file.rename(archive_path)
    
    print(f"✓ Archived: {{test_file}} -> {{archive_path}}")
else:
    print(f"✗ File not found: {{test_file}}")
'''
        return script.strip()
    
    def execute_action(self, recommendation: LifecycleRecommendation) -> bool:
        """
        Execute an automated lifecycle action.
        
        Returns: True if successful, False otherwise
        """
        if not recommendation.automated or not recommendation.script:
            return False
        
        try:
            # Execute Python script
            exec(recommendation.script)
            
            # Log action
            self._log_action(recommendation, success=True, result="Executed successfully")
            
            return True
        
        except Exception as e:
            # Log failure
            self._log_action(recommendation, success=False, result=str(e))
            return False
    
    def _log_action(self, recommendation: LifecycleRecommendation, 
                   success: bool, result: str):
        """Log lifecycle action to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO lifecycle_actions
            (action, target, reason, automated, executed, timestamp, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            recommendation.action.value,
            recommendation.target,
            recommendation.reason,
            recommendation.automated,
            success,
            datetime.now().isoformat(),
            result
        ))
        
        conn.commit()
        conn.close()
    
    def generate_lifecycle_report(self, recommendations: List[LifecycleRecommendation]) -> str:
        """Generate formatted lifecycle report"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("GU WU TEST LIFECYCLE MANAGEMENT REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTotal actions recommended: {len(recommendations)}")
        
        # Action type breakdown
        action_counts = {}
        for rec in recommendations:
            action_counts[rec.action] = action_counts.get(rec.action, 0) + 1
        
        lines.append(f"\nAction Distribution:")
        for action in LifecycleAction:
            count = action_counts.get(action, 0)
            if count > 0:
                automated = sum(1 for r in recommendations 
                              if r.action == action and r.automated)
                pct = (count / len(recommendations)) * 100
                lines.append(f"  {action.value.upper():10s}: {count:3d} actions ({pct:5.1f}%)")
                lines.append(f"               - {automated} automated, {count - automated} manual")
        
        # High priority actions (top 15)
        high_priority = [r for r in recommendations if r.priority in ['critical', 'high']]
        if high_priority:
            lines.append(f"\n{'-' * 80}")
            lines.append(f"HIGH-PRIORITY ACTIONS (top 15)")
            lines.append(f"{'-' * 80}")
            
            for i, rec in enumerate(high_priority[:15], 1):
                lines.append(f"\n{i}. {rec.action.value.upper()}: {rec.target}")
                lines.append(f"   Priority: {rec.priority.upper()}")
                lines.append(f"   Automated: {'Yes' if rec.automated else 'No'}")
                lines.append(f"   Reason: {rec.reason}")
                
                if rec.details.get('suggestions'):
                    lines.append(f"   Suggestions:")
                    for suggestion in rec.details['suggestions'][:3]:
                        lines.append(f"     - {suggestion}")
        
        # Automation summary
        automated_count = sum(1 for r in recommendations if r.automated)
        lines.append(f"\n{'-' * 80}")
        lines.append(f"AUTOMATION SUMMARY")
        lines.append(f"{'-' * 80}")
        lines.append(f"Total recommendations: {len(recommendations)}")
        lines.append(f"Automated: {automated_count} ({(automated_count/len(recommendations)*100):.1f}%)")
        lines.append(f"Manual: {len(recommendations) - automated_count}")
        
        lines.append(f"\n{'=' * 80}\n")
        
        return '\n'.join(lines)


# CLI interface
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Gu Wu Test Lifecycle Manager')
    parser.add_argument('--output', choices=['report', 'json'], default='report',
                       help='Output format')
    parser.add_argument('--execute-automated', action='store_true',
                       help='Execute all automated actions')
    parser.add_argument('--action-type', choices=['create', 'retire', 'refactor', 'update'],
                       help='Filter by action type')
    
    args = parser.parse_args()
    
    manager = TestLifecycleManager()
    
    # Analyze lifecycle
    recommendations = manager.analyze_lifecycle()
    
    # Filter by action type if specified
    if args.action_type:
        action_enum = LifecycleAction(args.action_type)
        recommendations = [r for r in recommendations if r.action == action_enum]
    
    if args.output == 'json':
        # JSON output
        output = {
            'total_actions': len(recommendations),
            'recommendations': [rec.to_dict() for rec in recommendations]
        }
        print(json.dumps(output, indent=2))
    
    else:
        # Human-readable report
        report = manager.generate_lifecycle_report(recommendations)
        print(report)
        
        # Save to file
        report_path = Path("tools/guwu/lifecycle_report.txt")
        report_path.write_text(report, encoding='utf-8')
        print(f"Report saved to: {report_path}")
    
    # Execute automated actions if requested
    if args.execute_automated:
        automated_actions = [r for r in recommendations if r.automated]
        
        if automated_actions:
            print("\n" + "=" * 80)
            print(f"EXECUTING {len(automated_actions)} AUTOMATED ACTIONS")
            print("=" * 80)
            
            success_count = 0
            for i, rec in enumerate(automated_actions, 1):
                print(f"\n{i}. {rec.action.value.upper()}: {rec.target}")
                
                if manager.execute_action(rec):
                    print(f"   ✓ Success")
                    success_count += 1
                else:
                    print(f"   ✗ Failed")
            
            print(f"\n{'=' * 80}")
            print(f"Executed: {success_count}/{len(automated_actions)} successful")
        else:
            print("\nNo automated actions to execute.")