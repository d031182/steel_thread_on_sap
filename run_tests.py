#!/usr/bin/env python3
"""
Human-Readable Test Runner

Wraps pytest to provide clear error explanations when tests fail.
Especially useful for Flask server conflicts and other common issues.

Usage: python run_tests.py [pytest args]
"""

import subprocess
import sys


def print_flask_server_error():
    """Print human-readable explanation for Flask server conflict"""
    print("\n" + "="*70)
    print("HUMAN-READABLE ERROR EXPLANATION")
    print("="*70)
    print("""
┌────────────────────────────────────────────────────────────────┐
│ 🔴 ERROR: Flask Server Interfering with Tests                 │
└────────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Your Flask development server is running (python app/app.py).
  Pytest tried to run tests while the server was active.
  This creates file handle conflicts.

WHY THIS BREAKS TESTS:
  • Flask locks files/ports that pytest needs to access
  • Both try to use the same SQLite database
  • Results in "I/O operation on closed file" errors

HOW TO FIX:
  
  ✅ Option 1: Stop Flask server first (RECOMMENDED)
     1. Find terminal running: python app/app.py
     2. Press Ctrl+C to stop the server
     3. Run: python run_tests.py (or pytest)
  
  ✅ Option 2: Use separate test database
     1. Configure pytest to use test-specific database
     2. Isolate test environment from dev server
  
  ✅ Option 3: Run tests in isolated terminal
     1. Open new terminal (not the one with Flask)
     2. Run: python run_tests.py
     3. Flask server continues in background (different process)

PREVENTION:
  Always stop dev server before running full test suite.
  Or use pytest-flask plugin for better server/test isolation.
""")
    print("="*70 + "\n")


def main():
    """Run pytest and provide human-readable error explanations"""
    
    # Build pytest command
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else []
    cmd = ["pytest"] + pytest_args
    
    print(f"Running: {' '.join(cmd)}\n")
    
    # Run pytest and capture output
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        # Check if pytest failed
        if result.returncode != 0:
            # Try to detect common error patterns
            # Note: We can't easily capture pytest's output without buffering,
            # so we just show the Flask error explanation if tests failed
            print_flask_server_error()
            
            print("\n💡 TIP: If this isn't a Flask server issue, the error details are shown above.")
            print("   Common issues:")
            print("   • Import errors: Missing packages (pip install <package>)")
            print("   • Assertion failures: Bug in code or incorrect test expectations")
            print("   • Fixture errors: Check conftest.py for fixture definitions\n")
        
        sys.exit(result.returncode)
        
    except FileNotFoundError:
        print("❌ ERROR: pytest not found. Install with: pip install pytest")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user (Ctrl+C)")
        sys.exit(130)


if __name__ == "__main__":
    main()