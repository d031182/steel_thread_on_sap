"""
Gu Wu Frontend Test Runner
===========================
Executes JavaScript unit tests and integrates results with Gu Wu metrics.

Part of Gu Wu Phase 8: Frontend Testing Extension
Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import subprocess
import json
import glob
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class FrontendTestRunner:
    """
    Discovers and executes frontend JavaScript unit tests.
    Integrates with Gu Wu metrics collection.
    """
    
    def __init__(self, base_path: str = "app/static/tests"):
        self.base_path = Path(base_path)
        self.unit_tests_path = self.base_path / "unit"
        
    def discover_tests(self) -> List[Path]:
        """
        Discover all frontend unit test files.
        
        Returns:
            List of test file paths
        """
        pattern = str(self.unit_tests_path / "**/*.test.js")
        test_files = [Path(f) for f in glob.glob(pattern, recursive=True)]
        return sorted(test_files)
    
    def run_test(self, test_file: Path) -> Dict:
        """
        Execute a single JavaScript test file.
        
        Args:
            test_file: Path to the test file
            
        Returns:
            Dictionary with test results:
            {
                'file': 'loggingPage.test.js',
                'passed': 18,
                'failed': 0,
                'duration': 0.45,
                'output': '...',
                'error': None
            }
        """
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ['node', str(test_file)],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=os.getcwd(),
                encoding='utf-8',  # Force UTF-8 encoding for Windows
                errors='replace'  # Replace undecodable chars
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Parse output for [PASS] and [FAIL] markers
            output = result.stdout
            passed = output.count('[PASS]')
            failed = output.count('[FAIL]')
            
            return {
                'file': test_file.name,
                'passed': passed,
                'failed': failed,
                'total': passed + failed,
                'duration': duration,
                'output': output,
                'error': result.stderr if result.returncode != 0 else None,
                'success': result.returncode == 0 and failed == 0
            }
            
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                'file': test_file.name,
                'passed': 0,
                'failed': 1,
                'total': 1,
                'duration': duration,
                'output': '',
                'error': f'Test timeout after 30 seconds',
                'success': False
            }
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                'file': test_file.name,
                'passed': 0,
                'failed': 1,
                'total': 1,
                'duration': duration,
                'output': '',
                'error': str(e),
                'success': False
            }
    
    def run_all_tests(self) -> Tuple[List[Dict], Dict]:
        """
        Run all discovered frontend tests.
        
        Returns:
            Tuple of (individual_results, summary)
            
        Example summary:
        {
            'total_files': 2,
            'total_tests': 38,
            'passed': 38,
            'failed': 0,
            'duration': 1.23,
            'success': True
        }
        """
        test_files = self.discover_tests()
        
        if not test_files:
            return [], {
                'total_files': 0,
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'duration': 0.0,
                'success': True,
                'message': 'No frontend tests found'
            }
        
        results = []
        total_passed = 0
        total_failed = 0
        total_duration = 0.0
        
        for test_file in test_files:
            result = self.run_test(test_file)
            results.append(result)
            
            total_passed += result['passed']
            total_failed += result['failed']
            total_duration += result['duration']
        
        summary = {
            'total_files': len(test_files),
            'total_tests': total_passed + total_failed,
            'passed': total_passed,
            'failed': total_failed,
            'duration': round(total_duration, 2),
            'success': total_failed == 0
        }
        
        return results, summary
    
    def format_results(self, results: List[Dict], summary: Dict) -> str:
        """
        Format test results for display.
        
        Args:
            results: Individual test results
            summary: Summary statistics
            
        Returns:
            Formatted string for console output
        """
        lines = []
        lines.append("\n" + "="*60)
        lines.append("FRONTEND JAVASCRIPT TESTS")
        lines.append("="*60)
        
        for result in results:
            status = "[PASS]" if result['success'] else "[FAIL]"  # ASCII-safe
            lines.append(f"\n{status} {result['file']}")
            lines.append(f"  Tests: {result['passed']} passed, {result['failed']} failed")
            lines.append(f"  Duration: {result['duration']:.2f}s")
            
            if result['error']:
                lines.append(f"  Error: {result['error']}")
        
        lines.append("\n" + "="*60)
        lines.append(f"Summary: {summary['passed']}/{summary['total_tests']} tests passed")
        lines.append(f"Files: {summary['total_files']}")
        lines.append(f"Duration: {summary['duration']}s")
        
        if summary['success']:
            lines.append("Status: [PASS] ALL TESTS PASSED")
        else:
            lines.append(f"Status: [FAIL] {summary['failed']} TESTS FAILED")
        
        lines.append("="*60 + "\n")
        
        return "\n".join(lines)


def run_frontend_tests(verbose: bool = True) -> bool:
    """
    Main entry point for running frontend tests.
    
    Args:
        verbose: Print detailed output
        
    Returns:
        True if all tests passed, False otherwise
    """
    runner = FrontendTestRunner()
    results, summary = runner.run_all_tests()
    
    if verbose:
        output = runner.format_results(results, summary)
        print(output)
    
    return summary['success']


if __name__ == "__main__":
    import sys
    success = run_frontend_tests(verbose=True)
    sys.exit(0 if success else 1)