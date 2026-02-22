"""
Feng Shui (风水) Unified CLI - Natural Language Entry Point

Provides simple, user-friendly commands for running Feng Shui analysis.

Usage Examples:
    python -m tools.fengshui                           # Show help
    python -m tools.fengshui analyze                   # Multi-agent analysis (6 agents)
    python -m tools.fengshui analyze --module knowledge_graph_v2
    python -m tools.fengshui fix                       # Autonomous ReAct agent batch fixes
    python -m tools.fengshui gate --module data_products_v2  # Quality gate validation
    python -m tools.fengshui critical                  # Critical security check only
    python -m tools.fengshui pre-commit                # Pre-commit validation
    python -m tools.fengshui pre-push                  # Pre-push validation

Philosophy: "Wind and water" - Harmonious flow in codebase architecture
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from enum import Enum


def show_banner():
    """Display Feng Shui banner"""
    print()
    print("=" * 70)
    print("  风水 FENG SHUI - Multi-Agent Architecture Intelligence")
    print("  'Wind and Water' - Harmonious Code Flow")
    print("=" * 70)
    print()


def analyze_command(args):
    """Run multi-agent comprehensive analysis (6 agents in parallel)"""
    show_banner()
    
    if args.module:
        module_path = Path(f"modules/{args.module}")
        if not module_path.exists():
            print(f"❌ Error: Module '{args.module}' not found")
            print(f"   Expected path: {module_path}")
            sys.exit(1)
        
        print(f"📦 Target: {args.module}")
    else:
        module_path = Path("modules")
        print(f"📦 Target: All modules")
    
    # Output file handling
    if args.output:
        output_path = Path(args.output)
        print(f"📄 Output: {output_path}")
    
    print()
    print("🔍 Running 7 specialized agents in parallel...")
    print("   1. Architecture Agent (DI violations, SOLID principles)")
    print("   2. Security Agent (hardcoded secrets, SQL injection)")
    print("   3. UX Architect Agent (SAP Fiori compliance)")
    print("   4. File Organization Agent (structure, obsolete files)")
    print("   5. Performance Agent (N+1 queries, caching)")
    print("   6. Documentation Agent (README quality, docstrings)")
    print("   7. Test Coverage Agent (API contracts, test quality)")
    print()
    
    # Import and run multi-agent analysis
    try:
        from tools.fengshui.react_agent import FengShuiReActAgent
        from tools.fengshui.utils import FindingFormatter
        
        agent = FengShuiReActAgent()
        report = agent.run_with_multiagent_analysis(
            module_path,
            parallel=not args.sequential
        )
        
        print()
        print("✅ Analysis Complete!")
        
        # Handle ComprehensiveReport object (dataclass)
        if hasattr(report, 'overall_health'):
            health_score = report.overall_health.get('score', 0) if isinstance(report.overall_health, dict) else getattr(report.overall_health, 'score', 0)
            print(f"   Overall Health: {health_score}/100")
        
        # Display findings with rich formatting (NEW in v4.34)
        if hasattr(report, 'findings_by_agent'):
            print(f"\n📊 Findings by Agent:")
            for agent_name, findings in report.findings_by_agent.items():
                count = len(findings) if isinstance(findings, list) else findings
                print(f"   {agent_name}: {count} findings")
            
            # Show detailed actionable findings if --detailed flag
            if args.detailed and hasattr(report, 'agent_reports'):
                print("\n" + "=" * 70)
                print("DETAILED FINDINGS (Actionable)")
                print("=" * 70)
                
                for agent_name, agent_report in report.agent_reports.items():
                    # Format with FindingFormatter (shows code + fixes)
                    formatted = FindingFormatter.format_agent_report(
                        agent_name,
                        agent_report,
                        show_full=True  # Full actionable view
                    )
                    print(formatted)
        
        # Save report to JSON file
        if args.output:
            import json
            from dataclasses import asdict, is_dataclass
            from pathlib import WindowsPath, PosixPath
            
            def serialize_report(obj):
                """Convert report object to JSON-serializable dict"""
                if is_dataclass(obj):
                    return serialize_report(asdict(obj))
                elif isinstance(obj, (WindowsPath, PosixPath, Path)):
                    return str(obj)
                elif isinstance(obj, Enum):
                    return obj.value
                elif isinstance(obj, dict):
                    return {k: serialize_report(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [serialize_report(item) for item in obj]
                else:
                    return obj
            
            output_path = Path(args.output)
            report_data = serialize_report(report)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n   Report saved to: {output_path}")
        else:
            # Default filename
            default_filename = f"feng_shui_report_{args.module or 'all'}.json"
            print(f"\n   Report saved to: {default_filename}")
        print()
        
        # Tip for users
        if not args.detailed:
            print("💡 Tip: Use --detailed flag to see actionable findings with code context and fixes")
            print("   Example: python -m tools.fengshui analyze --module knowledge_graph_v2 --detailed")
            print()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("   Multi-agent analysis requires Feng Shui Phase 4-17")
        sys.exit(1)


def fix_command(args):
    """Run autonomous ReAct agent for batch fixes"""
    show_banner()
    
    print("🤖 Autonomous ReAct Agent")
    print(f"   Target Score: {args.target_score}/100")
    print(f"   Max Iterations: {args.max_iterations}")
    print()
    print("🔧 Agent will autonomously:")
    print("   1. Detect architecture violations")
    print("   2. Create execution plan (dependency-aware)")
    print("   3. Execute fixes in parallel (up to 3x faster)")
    print("   4. Learn from outcomes, improve strategy")
    print()
    
    try:
        from tools.fengshui.react_agent import FengShuiReActAgent
        
        agent = FengShuiReActAgent()
        # Run autonomous agent (implementation depends on your ReAct agent)
        print("⚠️  Note: Use with caution - agent will modify files")
        print("   Recommendation: Commit current work first (git commit)")
        print()
        
        if input("Continue? (yes/no): ").lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
        
        # TODO: Implement autonomous fix workflow
        print("🚧 Autonomous fix workflow coming soon (Phase 4-18)")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def gate_command(args):
    """Run module quality gate validation"""
    show_banner()
    
    if not args.module:
        print("❌ Error: --module required for quality gate")
        print("   Example: python -m tools.fengshui gate --module knowledge_graph_v2")
        sys.exit(1)
    
    print(f"🚪 Quality Gate: {args.module}")
    print()
    
    try:
        from tools.fengshui.module_quality_gate import run_quality_gate
        
        exit_code = run_quality_gate(args.module)
        
        if exit_code == 0:
            print()
            print("✅ PASSED - Module ready for deployment")
        else:
            print()
            print("❌ FAILED - Fix violations before deployment")
        
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def critical_command(args):
    """Run critical security check only"""
    show_banner()
    
    print("🔒 Critical Security Check")
    print("   Checking for: SQL injection, hardcoded secrets, auth issues")
    print()
    
    try:
        from tools.fengshui.critical_check import run_critical_check
        
        exit_code = run_critical_check()
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def pre_commit_command(args):
    """Run pre-commit validation (fast, < 2s)"""
    show_banner()
    
    print("⚡ Pre-Commit Validation (< 2s target)")
    print("   Checking: File organization, critical security")
    print()
    
    try:
        from tools.fengshui.pre_commit_check import main as pre_commit_main
        
        pre_commit_main()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def pre_push_command(args):
    """Run pre-push validation (comprehensive, 35-80s)"""
    show_banner()
    
    print("🚀 Pre-Push Validation (35-80s target)")
    print("   Running: Full Feng Shui orchestrator analysis")
    print()
    
    try:
        from tools.fengshui.pre_push_analysis import main as pre_push_main
        
        pre_push_main()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Feng Shui (风水) - Multi-Agent Architecture Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Multi-agent analysis (6 agents, parallel execution)
  %(prog)s analyze
  %(prog)s analyze --module knowledge_graph_v2
  
  # Autonomous batch fixes (ReAct agent)
  %(prog)s fix --target-score 95
  
  # Quality gate validation (per-module)
  %(prog)s gate --module data_products_v2
  
  # Security-only check (fast)
  %(prog)s critical
  
  # Git hooks (automated)
  %(prog)s pre-commit   # < 2s
  %(prog)s pre-push     # 35-80s

Philosophy:
  Feng Shui (风水) means "Wind and Water" - the harmonious flow
  of energy. In code, this means maintaining clean architecture,
  proper dependency injection, and modular design patterns.
  
  7 Specialized Agents:
    1. Architecture  - DI violations, SOLID principles, coupling
    2. Security      - SQL injection, secrets, authentication
    3. UX Architect  - SAP Fiori compliance, UI/UX patterns
    4. FileOrg       - Structure, misplaced files, obsolete code
    5. Performance   - N+1 queries, caching, optimization
    6. Documentation - README quality, docstrings, comments
    7. TestCoverage  - API contracts (Gu Wu), test quality
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run multi-agent comprehensive analysis')
    analyze_parser.add_argument('--module', help='Target specific module (e.g., knowledge_graph_v2)')
    analyze_parser.add_argument('--sequential', action='store_true', help='Run agents sequentially instead of parallel')
    analyze_parser.add_argument('--detailed', action='store_true', help='Show detailed actionable findings with code context and fixes')
    analyze_parser.add_argument('--output', '-o', help='Output JSON file path (e.g., findings.json)')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Run autonomous ReAct agent for batch fixes')
    fix_parser.add_argument('--target-score', type=int, default=95, help='Target Feng Shui score (0-100)')
    fix_parser.add_argument('--max-iterations', type=int, default=10, help='Maximum fix iterations')
    
    # Gate command
    gate_parser = subparsers.add_parser('gate', help='Run module quality gate validation')
    gate_parser.add_argument('--module', required=True, help='Module to validate (e.g., data_products_v2)')
    
    # Critical command
    subparsers.add_parser('critical', help='Run critical security check only')
    
    # Pre-commit command
    subparsers.add_parser('pre-commit', help='Run pre-commit validation (fast, < 2s)')
    
    # Pre-push command
    subparsers.add_parser('pre-push', help='Run pre-push validation (comprehensive, 35-80s)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        show_banner()
        parser.print_help()
        sys.exit(0)
    
    # Execute command
    try:
        if args.command == 'analyze':
            analyze_command(args)
        elif args.command == 'fix':
            fix_command(args)
        elif args.command == 'gate':
            gate_command(args)
        elif args.command == 'critical':
            critical_command(args)
        elif args.command == 'pre-commit':
            pre_commit_command(args)
        elif args.command == 'pre-push':
            pre_push_command(args)
        
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