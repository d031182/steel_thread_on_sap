"""
Gu Wu CLI - Feng Shui Integration

Command-line interface for Feng Shui + Gu Wu resolution pipeline.

Usage:
    python -m tools.guwu.cli_feng_shui --agent file_organization --severity high
    python -m tools.guwu.cli_feng_shui --agent file_organization --dry-run
    python -m tools.guwu.cli_feng_shui --help

MED-25: Feng Shui + Gu Wu Integration Bridge
"""

import argparse
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.fengshui.agents.file_organization_agent import FileOrganizationAgent
from tools.guwu.resolvers.resolver_registry import ResolverRegistry
from tools.guwu.adapters import FengShuiAdapter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Feng Shui + Gu Wu Integration Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze and resolve file organization issues (HIGH+)
  python -m tools.guwu.cli_feng_shui --agent file_organization --severity high
  
  # Dry run (show what would be resolved without executing)
  python -m tools.guwu.cli_feng_shui --agent file_organization --dry-run
  
  # Resolve only specific categories
  python -m tools.guwu.cli_feng_shui --agent file_organization --categories "Root Directory Clutter"
  
  # Output JSON report
  python -m tools.guwu.cli_feng_shui --agent file_organization --json
        """
    )
    
    parser.add_argument(
        '--agent',
        default='file_organization',
        choices=['file_organization'],  # Add more agents as needed
        help='Feng Shui agent to run (default: file_organization)'
    )
    
    parser.add_argument(
        '--severity',
        default='medium',
        choices=['critical', 'high', 'medium', 'low'],
        help='Minimum severity to resolve (default: medium)'
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        help='Specific categories to resolve (e.g., "Root Directory Clutter")'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be resolved without executing'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    parser.add_argument(
        '--path',
        type=Path,
        default=Path('.'),
        help='Path to analyze (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Step 1: Run Feng Shui agent
    print("=" * 70)
    print(f"🔬 Feng Shui + Gu Wu Integration Pipeline")
    print("=" * 70)
    print()
    
    print(f"📊 Step 1: Running Feng Shui agent '{args.agent}'...")
    
    if args.agent == 'file_organization':
        agent = FileOrganizationAgent()
    else:
        print(f"❌ Unknown agent: {args.agent}")
        return 1
    
    report = agent.analyze_module(args.path)
    
    print(f"   ✅ Analysis complete: {len(report.findings)} findings")
    print(f"   📄 Summary: {report.summary}")
    print()
    
    # Step 2: Parse via adapter
    print(f"🔄 Step 2: Converting to Gu Wu format...")
    adapter = FengShuiAdapter()
    
    findings = adapter.parse_report(
        report,
        min_severity=args.severity,
        categories=args.categories
    )
    
    print(f"   ✅ Converted {len(findings)} findings >= '{args.severity}' severity")
    
    # Show summary
    summary = adapter.get_summary(findings)
    print(f"   📊 Summary: {summary['critical']} critical, {summary['high']} high, "
          f"{summary['medium']} medium, {summary['low']} low")
    print()
    
    if len(findings) == 0:
        print("✨ No findings to resolve!")
        return 0
    
    # Step 3: Group by category
    grouped = adapter.group_by_category(findings)
    print(f"📦 Step 3: Grouped into {len(grouped)} categories:")
    for category, cat_findings in grouped.items():
        print(f"   - {category}: {len(cat_findings)} findings")
    print()
    
    # Step 4: Resolve with Gu Wu
    print(f"🔧 Step 4: Resolving with Gu Wu...")
    print()
    
    registry = ResolverRegistry()
    registry.discover_resolvers()
    
    results = registry.process_feng_shui_report(
        report,
        min_severity=args.severity,
        dry_run=args.dry_run
    )
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print("=" * 70)
        print("✅ Resolution Complete!")
        print("=" * 70)
        print(f"Total findings: {results['total_findings']}")
        print(f"Resolved: {results['resolved']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
        print()
        
        if results['results']:
            print("Details:")
            for result in results['results']:
                status_emoji = {
                    'resolved': '✅',
                    'failed': '❌',
                    'skipped': '⏭️',
                    'dry_run': '👀',
                    'error': '💥'
                }.get(result['status'], '❓')
                
                print(f"  {status_emoji} {result['category']}: {result.get('description', 'N/A')}")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
    
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())