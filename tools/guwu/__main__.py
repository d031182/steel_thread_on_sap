"""
Gu Wu (顾武) Unified CLI - Natural Language Entry Point

Provides simple, user-friendly commands for running Gu Wu test intelligence.

Usage Examples:
    python -m tools.guwu                           # Show help
    python -m tools.guwu run                       # Run all tests with optimization
    python -m tools.guwu intelligence              # Show Intelligence Hub report
    python -m tools.guwu dashboard                 # Show health dashboard
    python -m tools.guwu recommend                 # Get actionable recommendations
    python -m tools.guwu predict                   # ML failure prediction + pre-flight
    python -m tools.guwu gaps                      # Show test coverage gaps
    python -m tools.guwu metrics                   # Show detailed metrics

Philosophy: "Attending to martial affairs" - Disciplined, self-healing tests
"""

import argparse
import sys
from pathlib import Path


def show_banner():
    """Display Gu Wu banner"""
    print()
    print("=" * 70)
    print("  顾武 GU WU - Self-Healing Test Intelligence")
    print("  'Attending to Martial Affairs' - Disciplined Testing")
    print("=" * 70)
    print()


def run_command(args):
    """Run tests with Gu Wu optimization"""
    show_banner()
    
    print("🧪 Running Test Suite with Gu Wu Optimization")
    print()
    print("📊 Test Pyramid Enforcement:")
    print("   70% Unit Tests (fast, isolated)")
    print("   20% Integration Tests (module interactions)")
    print("   10% E2E Tests (critical workflows)")
    print()
    print("🎯 Features:")
    print("   • Auto-prioritization (likely-to-fail tests first)")
    print("   • Flaky test detection (transition-based algorithm)")
    print("   • Performance tracking (slow tests flagged > 5s)")
    print("   • Gap detection (untested code identified)")
    print("   • Meta-learning (learns from execution history)")
    print()
    
    # Run pytest with Gu Wu hooks
    import subprocess
    
    test_args = []
    if args.path:
        test_args.append(args.path)
    if args.verbose:
        test_args.append('-v')
    if args.markers:
        test_args.extend(['-m', args.markers])
    
    cmd = ['pytest'] + test_args
    print(f"💻 Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def intelligence_command(args):
    """Show Intelligence Hub comprehensive report"""
    show_banner()
    
    print("🧠 Intelligence Hub - Comprehensive Test Analysis")
    print()
    print("   Combines all 3 intelligence engines:")
    print("   1. Recommendations Engine (8 types of insights)")
    print("   2. Dashboard Engine (visual health metrics + trends)")
    print("   3. Predictive Engine (ML failure forecasting)")
    print()
    
    try:
        # Import and run intelligence hub
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 
            'tests.guwu.intelligence.intelligence_hub'
        ])
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Intelligence Hub requires Gu Wu Phase 7")
        sys.exit(1)


def dashboard_command(args):
    """Show health dashboard with trends"""
    show_banner()
    
    print("📊 Test Suite Health Dashboard")
    print()
    print("   Visual metrics:")
    print("   • Overall health score (0-100)")
    print("   • Failure rate trends (7/30 day moving average)")
    print("   • Execution time trends (performance monitoring)")
    print("   • Flaky test score distribution")
    print("   • Coverage percentage over time")
    print()
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m',
            'tests.guwu.intelligence.dashboard'
        ])
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def recommend_command(args):
    """Get actionable recommendations"""
    show_banner()
    
    print("💡 Actionable Recommendations")
    print()
    print("   8 types of insights:")
    print("   1. Flaky tests (prioritized by impact)")
    print("   2. Slow tests (> 5s threshold)")
    print("   3. Failing tests (recent failures)")
    print("   4. Coverage gaps (untested code)")
    print("   5. Test debt (accumulating issues)")
    print("   6. Maintenance needs (code smells)")
    print("   7. Optimization opportunities (parallelization)")
    print("   8. Best practices (test quality)")
    print()
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m',
            'tests.guwu.intelligence.recommendations'
        ])
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def predict_command(args):
    """ML failure prediction + pre-flight check"""
    show_banner()
    
    print("🔮 Predictive Analytics - ML Failure Forecasting")
    print()
    print("   Capabilities:")
    print("   • Pre-flight check (predict failures before commit)")
    print("   • Failure probability (ML-powered forecasting)")
    print("   • Historical pattern analysis (learns over time)")
    print("   • Risk assessment (confidence scores)")
    print()
    
    if args.pre_flight:
        print("🚀 Running Pre-Flight Check...")
        print("   Analyzing uncommitted changes for failure risk")
        print()
    
    try:
        import subprocess
        cmd = [sys.executable, '-m', 'tests.guwu.intelligence.predictive']
        if args.pre_flight:
            cmd.append('--pre-flight')
        
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def gaps_command(args):
    """Show test coverage gaps"""
    show_banner()
    
    print("🔍 Test Coverage Gap Analysis")
    print()
    print("   Detects:")
    print("   • Missing test files (untested modules)")
    print("   • Incomplete coverage (< 70% threshold)")
    print("   • Untested functions/classes")
    print("   • Critical code without tests")
    print()
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m',
            'tools.guwu.test_gap_display'
        ])
        sys.exit(result.returncode)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def metrics_command(args):
    """Show detailed test metrics"""
    show_banner()
    
    print("📈 Detailed Test Metrics")
    print()
    print("   Metrics tracked:")
    print("   • Test execution history (pass/fail/skip)")
    print("   • Duration tracking (performance trends)")
    print("   • Flakiness scores (0.0-1.0 scale)")
    print("   • Coverage percentages (per module)")
    print("   • Learning events (meta-learning insights)")
    print()
    
    try:
        # Query metrics database
        from tools.guwu.metrics import TestMetrics
        
        metrics = TestMetrics()
        print("📊 Recent Test Metrics:")
        print()
        # TODO: Implement metrics display
        print("🚧 Detailed metrics display coming soon")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Gu Wu (顾武) - Self-Healing Test Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run tests with optimization
  %(prog)s run
  %(prog)s run tests/unit/
  %(prog)s run -v -m "unit and fast"
  
  # Intelligence Hub (comprehensive report)
  %(prog)s intelligence
  
  # Individual engines
  %(prog)s dashboard       # Visual health metrics
  %(prog)s recommend       # Actionable insights
  %(prog)s predict         # ML failure forecasting
  %(prog)s predict --pre-flight  # Pre-commit check
  
  # Analysis tools
  %(prog)s gaps           # Test coverage gaps
  %(prog)s metrics        # Detailed metrics

Philosophy:
  Gu Wu (顾武) means "Attending to Martial Affairs" - maintaining
  discipline and readiness. In testing, this means self-healing,
  self-optimizing test suites that learn and improve over time.
  
  Phase 7 Intelligence Engines:
    1. Recommendations - 8 types of actionable insights
    2. Dashboard - Visual health metrics with trends
    3. Predictive - ML-powered failure forecasting
  
  Test Pyramid (enforced automatically):
    70%% Unit Tests      - Fast, isolated (< 1s each)
    20%% Integration     - Module interactions (< 5s each)
    10%% E2E Tests       - Critical workflows (< 30s each)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run tests with Gu Wu optimization')
    run_parser.add_argument('path', nargs='?', help='Test path (default: all tests)')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    run_parser.add_argument('-m', '--markers', help='Pytest markers (e.g., "unit and fast")')
    
    # Intelligence command
    subparsers.add_parser('intelligence', help='Show Intelligence Hub comprehensive report')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Show health dashboard with trends')
    
    # Recommend command
    subparsers.add_parser('recommend', help='Get actionable recommendations')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='ML failure prediction + pre-flight')
    predict_parser.add_argument('--pre-flight', action='store_true', help='Run pre-flight check before commit')
    
    # Gaps command
    subparsers.add_parser('gaps', help='Show test coverage gaps')
    
    # Metrics command
    subparsers.add_parser('metrics', help='Show detailed test metrics')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        show_banner()
        parser.print_help()
        sys.exit(0)
    
    # Execute command
    try:
        if args.command == 'run':
            run_command(args)
        elif args.command == 'intelligence':
            intelligence_command(args)
        elif args.command == 'dashboard':
            dashboard_command(args)
        elif args.command == 'recommend':
            recommend_command(args)
        elif args.command == 'predict':
            predict_command(args)
        elif args.command == 'gaps':
            gaps_command(args)
        elif args.command == 'metrics':
            metrics_command(args)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()