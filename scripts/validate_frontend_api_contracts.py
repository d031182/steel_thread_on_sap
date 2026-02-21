#!/usr/bin/env python3
"""
Frontend API Contract Validation Script

Purpose: Validate all frontend API contracts in CI/CD pipeline
- Runs all @pytest.mark.api_contract tests
- Reports contract violations
- Returns non-zero exit code on failures
- Suitable for build stage integration

Usage:
    python scripts/validate_frontend_api_contracts.py [--verbose]

Exit Codes:
    0 = All contracts valid
    1 = Contract violations detected
    2 = Configuration/runtime error
"""

import subprocess
import sys
from pathlib import Path


def run_contract_tests(verbose=False):
    """Run all frontend API contract tests via pytest"""
    
    print("=" * 70)
    print("Frontend API Contract Validation")
    print("=" * 70)
    
    # Build pytest command
    cmd = [
        "pytest",
        "tests/",
        "-m", "api_contract",
        "-v" if verbose else "-q",
        "--tb=short",
        "-x",  # Stop on first failure
    ]
    
    print(f"\n📋 Running command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("\n" + "=" * 70)
            print("✅ All frontend API contracts validated successfully")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ Frontend API contract violations detected")
            print("=" * 70)
            return 1
            
    except FileNotFoundError:
        print("❌ Error: pytest not found. Install with: pip install pytest")
        return 2
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 2


def main():
    """Main entry point"""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    exit_code = run_contract_tests(verbose=verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()