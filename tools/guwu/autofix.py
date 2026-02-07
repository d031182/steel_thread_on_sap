"""
Gu Wu Auto-Fix Generator - Stage 2 of Phase 3

Analyzes test failures and generates fix suggestions automatically.
Pattern-based matching + AI-inspired analysis for common failure types.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class FixType(Enum):
    """Types of fixes"""
    AUTO_FIXABLE = "auto_fixable"        # Can be applied automatically
    MANUAL_REQUIRED = "manual_required"  # Requires human intervention
    SUGGESTION = "suggestion"            # Suggestion, not a guaranteed fix


@dataclass
class FixSuggestion:
    """A suggested fix for a test failure"""
    failure_type: str           # Type of failure (assertion, import, etc.)
    fix_type: FixType           # Auto-fixable or manual
    description: str            # Human-readable description
    code_diff: Optional[str]    # Actual code changes (if auto-fixable)
    manual_steps: Optional[str] # Manual steps (if manual required)
    confidence: float           # Confidence in fix (0.0-1.0)
    reason: str                 # Why this fix should work
    test_command: Optional[str] # Command to test the fix
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'failure_type': self.failure_type,
            'fix_type': self.fix_type.value,
            'description': self.description,
            'code_diff': self.code_diff,
            'manual_steps': self.manual_steps,
            'confidence': round(self.confidence, 2),
            'reason': self.reason,
            'test_command': self.test_command
        }


class AutoFixGenerator:
    """
    Generates fix suggestions for common test failures.
    
    Pattern Categories:
    1. Assertion Errors (value mismatches)
    2. Import Errors (missing modules, renamed APIs)
    3. Attribute Errors (missing/renamed methods)
    4. Type Errors (wrong types passed)
    5. Timeout Errors (slow tests)
    6. File Not Found (missing test data)
    7. Flaky Tests (race conditions)
    """
    
    # Pattern database - maps error patterns to fix strategies
    PATTERNS = {
        'assertion_error': {
            'regex': r'AssertionError: assert (.*?) == (.*?)$',
            'description': 'Expected value mismatch',
            'fix_type': FixType.AUTO_FIXABLE,
            'confidence': 0.9,
            'handler': '_fix_assertion_error'
        },
        'assert_in': {
            'regex': r'AssertionError: assert (.*?) in (.*?)$',
            'description': 'Value not in expected collection',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.7,
            'handler': '_fix_assert_in'
        },
        'import_error': {
            'regex': r'ImportError: cannot import name \'(.*?)\' from \'(.*?)\'',
            'description': 'Missing or renamed import',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.8,
            'handler': '_fix_import_error'
        },
        'module_not_found': {
            'regex': r'ModuleNotFoundError: No module named \'(.*?)\'',
            'description': 'Missing dependency',
            'fix_type': FixType.AUTO_FIXABLE,
            'confidence': 0.95,
            'handler': '_fix_module_not_found'
        },
        'attribute_error': {
            'regex': r'AttributeError: .*? has no attribute \'(.*?)\'',
            'description': 'Method/attribute renamed or removed',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.6,
            'handler': '_fix_attribute_error'
        },
        'type_error': {
            'regex': r'TypeError: (.*?)$',
            'description': 'Wrong type passed to function',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.7,
            'handler': '_fix_type_error'
        },
        'timeout_error': {
            'regex': r'(TimeoutError|timed? out)',
            'description': 'Test execution timeout',
            'fix_type': FixType.AUTO_FIXABLE,
            'confidence': 0.85,
            'handler': '_fix_timeout_error'
        },
        'file_not_found': {
            'regex': r'FileNotFoundError: \[Errno 2\] No such file or directory: \'(.*?)\'',
            'description': 'Missing test data file',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.9,
            'handler': '_fix_file_not_found'
        },
        'key_error': {
            'regex': r'KeyError: \'(.*?)\'',
            'description': 'Missing dictionary key',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.75,
            'handler': '_fix_key_error'
        },
        'index_error': {
            'regex': r'IndexError: (list index out of range|.*?)$',
            'description': 'List/array index out of bounds',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.7,
            'handler': '_fix_index_error'
        },
        'zero_division': {
            'regex': r'ZeroDivisionError: division by zero',
            'description': 'Division by zero',
            'fix_type': FixType.MANUAL_REQUIRED,
            'confidence': 0.8,
            'handler': '_fix_zero_division'
        }
    }
    
    def __init__(self, db_path: str = "tools/guwu/metrics.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Metrics database not found: {db_path}")
        
        # Fix history database (learning)
        self._init_fix_database()
    
    def _init_fix_database(self):
        """Initialize fix history database for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fix suggestions history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fix_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT NOT NULL,
                failure_type TEXT NOT NULL,
                fix_type TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                code_diff TEXT,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                applied BOOLEAN DEFAULT 0,
                worked BOOLEAN DEFAULT NULL,
                feedback TEXT
            )
        ''')
        
        # Fix success rate (for learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fix_statistics (
                failure_type TEXT PRIMARY KEY,
                total_suggestions INTEGER DEFAULT 0,
                successful_fixes INTEGER DEFAULT 0,
                failed_fixes INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_fix(self, test_id: str, error_message: str, 
                    test_file: Optional[str] = None) -> FixSuggestion:
        """
        Generate fix suggestion for a test failure.
        
        Args:
            test_id: Test identifier
            error_message: Full error message from test failure
            test_file: Path to test file (optional, for context)
        
        Returns:
            FixSuggestion with details
        """
        # Try pattern matching first
        for pattern_name, pattern_info in self.PATTERNS.items():
            match = re.search(pattern_info['regex'], error_message, re.MULTILINE)
            if match:
                # Call specific handler
                handler_name = pattern_info['handler']
                handler = getattr(self, handler_name)
                
                fix = handler(pattern_name, match, error_message, test_id, test_file)
                
                # Store suggestion in database
                self._store_suggestion(test_id, fix)
                
                return fix
        
        # Fallback: Generic analysis
        return self._generic_fix_suggestion(test_id, error_message, test_file)
    
    # ========== Specific Fix Handlers ==========
    
    def _fix_assertion_error(self, pattern_name: str, match: re.Match, 
                            error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix assertion error (value mismatch)"""
        
        actual = match.group(1).strip()
        expected = match.group(2).strip()
        
        # Generate code diff
        code_diff = f"""
# In {test_file or 'test file'}:
# OLD:
assert {actual} == {expected}

# NEW (Option 1 - Update expected value):
assert {actual} == {actual}  # Updated to match actual

# NEW (Option 2 - Fix the code being tested):
# Review why {actual} != {expected} and fix the implementation
"""
        
        return FixSuggestion(
            failure_type='assertion_error',
            fix_type=FixType.AUTO_FIXABLE,
            description=f"Assertion failed: expected {expected}, got {actual}",
            code_diff=code_diff,
            manual_steps=None,
            confidence=0.9,
            reason="Common assertion failure - either update expected value or fix implementation",
            test_command=f"pytest {test_id} -v"
        )
    
    def _fix_assert_in(self, pattern_name: str, match: re.Match,
                      error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix 'assert X in Y' failure"""
        
        value = match.group(1).strip()
        collection = match.group(2).strip()
        
        manual_steps = f"""
1. Check what's actually in {collection}
2. Verify {value} is the correct expected value
3. Fix either the test data or the assertion
4. Consider using `assert {value} in {collection}, f"{value} not found. Got: {{{collection}}}"` for better error messages
"""
        
        return FixSuggestion(
            failure_type='assert_in',
            fix_type=FixType.MANUAL_REQUIRED,
            description=f"Value {value} not found in {collection}",
            code_diff=None,
            manual_steps=manual_steps,
            confidence=0.7,
            reason="Value missing from collection - check test data or implementation",
            test_command=f"pytest {test_id} -v"
        )
    
    def _fix_import_error(self, pattern_name: str, match: re.Match,
                         error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix import error (missing/renamed module)"""
        
        name = match.group(1)
        module = match.group(2)
        
        manual_steps = f"""
1. Check if '{name}' was renamed in '{module}'
2. Search codebase for new name: grep -r "{name}" {module.replace('.', '/')}
3. Update import statement
4. If module doesn't exist, check if it was moved or deleted
5. Update requirements.txt if external dependency
"""
        
        return FixSuggestion(
            failure_type='import_error',
            fix_type=FixType.MANUAL_REQUIRED,
            description=f"Cannot import '{name}' from '{module}'",
            code_diff=None,
            manual_steps=manual_steps,
            confidence=0.8,
            reason="Import may be renamed, moved, or missing - requires investigation",
            test_command=None
        )
    
    def _fix_module_not_found(self, pattern_name: str, match: re.Match,
                             error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix module not found (missing dependency)"""
        
        module = match.group(1)
        
        # Common module → package mapping
        package_map = {
            'pytest': 'pytest',
            'flask': 'Flask',
            'requests': 'requests',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'sqlalchemy': 'SQLAlchemy'
        }
        
        package = package_map.get(module, module)
        
        code_diff = f"""
# Install missing package:
pip install {package}

# Or add to requirements.txt:
echo "{package}" >> requirements.txt
pip install -r requirements.txt
"""
        
        return FixSuggestion(
            failure_type='module_not_found',
            fix_type=FixType.AUTO_FIXABLE,
            description=f"Missing Python package: {module}",
            code_diff=code_diff,
            manual_steps=None,
            confidence=0.95,
            reason=f"Package {module} not installed - add to dependencies",
            test_command=f"pip install {package} && pytest {test_id} -v"
        )
    
    def _fix_attribute_error(self, pattern_name: str, match: re.Match,
                            error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix attribute error (missing method/property)"""
        
        attr_name = match.group(1)
        
        manual_steps = f"""
1. Search for old method/property name '{attr_name}' in git history
2. Check if it was renamed: git log --all -S"{attr_name}" --source --
3. Update test to use new method/property name
4. Check API documentation for current interface
5. If method was removed, find alternative approach
"""
        
        return FixSuggestion(
            failure_type='attribute_error',
            fix_type=FixType.MANUAL_REQUIRED,
            description=f"Method/attribute '{attr_name}' not found",
            code_diff=None,
            manual_steps=manual_steps,
            confidence=0.6,
            reason="API may have changed - check documentation and git history",
            test_command=None
        )
    
    def _fix_type_error(self, pattern_name: str, match: re.Match,
                       error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix type error (wrong type passed)"""
        
        error_detail = match.group(1)
        
        manual_steps = f"""
1. Read error details: {error_detail}
2. Check function signature for expected types
3. Add type hints if missing: def func(param: ExpectedType) -> ReturnType
4. Fix caller to pass correct type
5. Consider adding type validation in function
"""
        
        return FixSuggestion(
            failure_type='type_error',
            fix_type=FixType.MANUAL_REQUIRED,
            description=f"Type error: {error_detail}",
            code_diff=None,
            manual_steps=manual_steps,
            confidence=0.7,
            reason="Wrong type passed - check function signature and caller",
            test_command=f"pytest {test_id} -v"
        )
    
    def _fix_timeout_error(self, pattern_name: str, match: re.Match,
                          error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix timeout error (slow test)"""
        
        code_diff = f"""
# Option 1: Increase timeout (quick fix)
@pytest.mark.timeout(30)  # Increase from default
def {test_id.split('::')[-1]}():
    ...

# Option 2: Optimize test (better fix)
# - Mock slow external dependencies
# - Reduce test data size
# - Use fixtures to reuse expensive setup
# - Move to integration test layer if testing I/O

# Option 3: Mark as slow test
@pytest.mark.slow
def {test_id.split('::')[-1]}():
    ...
"""
        
        return FixSuggestion(
            failure_type='timeout_error',
            fix_type=FixType.AUTO_FIXABLE,
            description="Test execution timeout",
            code_diff=code_diff,
            manual_steps=None,
            confidence=0.85,
            reason="Test too slow - increase timeout or optimize test execution",
            test_command=f"pytest {test_id} -v --timeout=30"
        )
    
    def _fix_file_not_found(self, pattern_name: str, match: re.Match,
                           error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix file not found error (missing test data)"""
        
        file_path = match.group(1)
        
        manual_steps = f"""
1. Check if test data file exists: ls -la {file_path}
2. Verify correct path (relative vs absolute)
3. Check if file was moved: git log --all -- {file_path}
4. Create missing test data file if needed
5. Update path in test if file was moved
6. Add file to version control if missing
"""
        
        return FixSuggestion(
            failure_type='file_not_found',
            fix_type=FixType.MANUAL_REQUIRED,
            description=f"Missing test data file: {file_path}",
            code_diff=None,
            manual_steps=manual_steps,
            confidence=0.9,
            reason="Test data file missing or path incorrect",
            test_command=None
        )
    
    def _fix_key_error(self, pattern_name: str, match: re.Match,
                      error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix key error (missing dict key)"""
        
        key = match.group(1)
        
        code_diff = f"""
# Option 1: Use .get() with default
value = my_dict.get('{key}', default_value)

# Option 2: Check key exists
if '{key}' in my_dict:
    value = my_dict['{key}']

# Option 3: Fix test data to include key
test_data = {{
    '{key}': expected_value,
    ...
}}
"""
        
        return FixSuggestion(
            failure_type='key_error',
            fix_type=FixType.MANUAL_REQUIRED,
            description=f"Missing dictionary key: '{key}'",
            code_diff=code_diff,
            manual_steps=None,
            confidence=0.75,
            reason="Dictionary missing expected key - check test data or use .get()",
            test_command=f"pytest {test_id} -v"
        )
    
    def _fix_index_error(self, pattern_name: str, match: re.Match,
                        error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix index error (list index out of bounds)"""
        
        code_diff = """
# Option 1: Check list length before accessing
if len(my_list) > index:
    value = my_list[index]

# Option 2: Use try/except
try:
    value = my_list[index]
except IndexError:
    value = default_value

# Option 3: Fix test data to have correct length
"""
        
        return FixSuggestion(
            failure_type='index_error',
            fix_type=FixType.MANUAL_REQUIRED,
            description="List index out of range",
            code_diff=code_diff,
            manual_steps=None,
            confidence=0.7,
            reason="Accessing index beyond list length - check bounds or test data",
            test_command=f"pytest {test_id} -v"
        )
    
    def _fix_zero_division(self, pattern_name: str, match: re.Match,
                          error_msg: str, test_id: str, test_file: Optional[str]) -> FixSuggestion:
        """Fix zero division error"""
        
        code_diff = """
# Add zero check before division:
if denominator != 0:
    result = numerator / denominator
else:
    result = 0  # or handle appropriately

# Or use conditional expression:
result = numerator / denominator if denominator != 0 else 0
"""
        
        return FixSuggestion(
            failure_type='zero_division',
            fix_type=FixType.MANUAL_REQUIRED,
            description="Division by zero",
            code_diff=code_diff,
            manual_steps=None,
            confidence=0.8,
            reason="Check denominator before division or fix test data",
            test_command=f"pytest {test_id} -v"
        )
    
    def _generic_fix_suggestion(self, test_id: str, error_msg: str, 
                                test_file: Optional[str]) -> FixSuggestion:
        """Fallback for unknown error patterns"""
        
        manual_steps = f"""
1. Read full error message carefully
2. Check stack trace for root cause
3. Search error message online: "{error_msg[:100]}"
4. Review recent code changes in test file
5. Run test in isolation: pytest {test_id} -v -s
6. Add debug logging to understand failure
"""
        
        return FixSuggestion(
            failure_type='unknown',
            fix_type=FixType.SUGGESTION,
            description="Unknown failure pattern",
            code_diff=None,
            manual_steps=manual_steps,
            confidence=0.3,
            reason="Error pattern not recognized - requires manual investigation",
            test_command=f"pytest {test_id} -v -s"
        )
    
    def _store_suggestion(self, test_id: str, fix: FixSuggestion):
        """Store fix suggestion in database for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fix_suggestions
            (test_id, failure_type, fix_type, suggestion, code_diff, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_id,
            fix.failure_type,
            fix.fix_type.value,
            fix.description,
            fix.code_diff,
            fix.confidence,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def record_fix_result(self, test_id: str, worked: bool, feedback: Optional[str] = None):
        """
        Record whether a fix worked (for learning).
        
        Args:
            test_id: Test that was fixed
            worked: True if fix resolved the issue
            feedback: Optional feedback on the fix
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update most recent suggestion for this test
        cursor.execute('''
            UPDATE fix_suggestions
            SET applied = 1, worked = ?, feedback = ?
            WHERE test_id = ?
            AND id = (
                SELECT id FROM fix_suggestions
                WHERE test_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            )
        ''', (worked, feedback, test_id, test_id))
        
        # Update statistics
        cursor.execute('''
            SELECT failure_type FROM fix_suggestions
            WHERE test_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (test_id,))
        
        result = cursor.fetchone()
        if result:
            failure_type = result[0]
            
            cursor.execute('''
                INSERT INTO fix_statistics (failure_type, total_suggestions, successful_fixes, failed_fixes)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(failure_type) DO UPDATE SET
                    total_suggestions = total_suggestions + 1,
                    successful_fixes = successful_fixes + ?,
                    failed_fixes = failed_fixes + ?,
                    success_rate = CAST(successful_fixes AS REAL) / total_suggestions
            ''', (
                failure_type,
                1 if worked else 0,
                0 if worked else 1,
                1 if worked else 0,
                0 if worked else 1
            ))
        
        conn.commit()
        conn.close()
    
    def get_fix_success_rate(self, failure_type: Optional[str] = None) -> Dict:
        """Get success rate statistics for fixes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if failure_type:
            cursor.execute('''
                SELECT failure_type, total_suggestions, successful_fixes, 
                       failed_fixes, success_rate
                FROM fix_statistics
                WHERE failure_type = ?
            ''', (failure_type,))
        else:
            cursor.execute('''
                SELECT failure_type, total_suggestions, successful_fixes,
                       failed_fixes, success_rate
                FROM fix_statistics
                ORDER BY success_rate DESC
            ''')
        
        results = {}
        for row in cursor.fetchall():
            results[row[0]] = {
                'total_suggestions': row[1],
                'successful_fixes': row[2],
                'failed_fixes': row[3],
                'success_rate': round(row[4], 2) if row[4] else 0.0
            }
        
        conn.close()
        return results


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gu Wu Auto-Fix Generator')
    parser.add_argument('--test-id', required=True, help='Test ID that failed')
    parser.add_argument('--error', required=True, help='Error message')
    parser.add_argument('--test-file', help='Path to test file')
    parser.add_argument('--record-result', choices=['worked', 'failed'], help='Record fix result')
    parser.add_argument('--stats', action='store_true', help='Show fix statistics')
    
    args = parser.parse_args()
    
    generator = AutoFixGenerator()
    
    if args.stats:
        # Show statistics
        stats = generator.get_fix_success_rate()
        print("\n" + "=" * 80)
        print("GU WU AUTO-FIX SUCCESS RATE STATISTICS")
        print("=" * 80)
        
        for failure_type, data in stats.items():
            print(f"\n{failure_type.upper()}:")
            print(f"  Total Suggestions: {data['total_suggestions']}")
            print(f"  Successful: {data['successful_fixes']}")
            print(f"  Failed: {data['failed_fixes']}")
            print(f"  Success Rate: {data['success_rate']:.1%}")
        
        print("\n" + "=" * 80)
    
    elif args.record_result:
        # Record fix result
        worked = args.record_result == 'worked'
        generator.record_fix_result(args.test_id, worked)
        print(f"✓ Recorded: Fix {'worked' if worked else 'failed'} for {args.test_id}")
    
    else:
        # Generate fix suggestion
        fix = generator.generate_fix(args.test_id, args.error, args.test_file)
        
        print("\n" + "=" * 80)
        print("GU WU AUTO-FIX SUGGESTION")
        print("=" * 80)
        print(f"\nTest: {args.test_id}")
        print(f"Failure Type: {fix.failure_type}")
        print(f"Fix Type: {fix.fix_type.value}")
        print(f"Confidence: {fix.confidence:.1%}")
        print(f"\nDescription: {fix.description}")
        print(f"\nReason: {fix.reason}")
        
        if fix.code_diff:
            print(f"\nCode Changes:")
            print(fix.code_diff)
        
        if fix.manual_steps:
            print(f"\nManual Steps:")
            print(fix.manual_steps)
        
        if fix.test_command:
            print(f"\nTest Command:")
            print(f"  {fix.test_command}")
        
        print("\n" + "=" * 80)
        print(f"\nTo record if this fix worked:")
        print(f"  python -m tests.guwu.autofix --test-id '{args.test_id}' --error '...' --record-result worked")
        print(f"  python -m tests.guwu.autofix --test-id '{args.test_id}' --error '...' --record-result failed")
        print("")