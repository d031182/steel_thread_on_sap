"""
Shi Fu Unified CLI - Phase 7

Single entry point for all enhancement consultation workflows.

Usage:
    # Consult on Feng Shui (code quality) gaps
    python -m tools.shifu.meta.unified_cli consult --fengshui "Empty directories"
    
    # Consult on Gu Wu (test quality) gaps
    python -m tools.shifu.meta.unified_cli consult --guwu "Add E2E tests"
    
    # Auto-discovery check (finds new agents/capabilities)
    python -m tools.shifu.meta.unified_cli discover
    
    # Architecture observation (finds gaps automatically)
    python -m tools.shifu.meta.unified_cli observe --fengshui
    python -m tools.shifu.meta.unified_cli observe --guwu
    
    # Session start (integrated with shifu --session-start)
    python -m tools.shifu.meta.unified_cli session-start
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Import consultation modules
from .enhancement_proposer import EnhancementProposer
from .guwu_enhancement_proposer import GuWuEnhancementProposer
from .agent_auto_discovery import AgentAutoDiscovery
from .architecture_observer import ArchitectureObserver


def consult_fengshui(issue: str) -> None:
    """Generate Feng Shui (code quality) enhancement proposal"""
    print()
    print("=" * 70)
    print("Shi Fu Feng Shui Consultation")
    print("=" * 70)
    print()
    print(f"Issue: {issue}")
    print()
    
    proposer = EnhancementProposer()
    proposal = proposer.analyze_gap(issue)
    
    print(f"✅ Proposal Generated!")
    print(f"   ID: {proposal.proposal_id}")
    print(f"   Agent: {proposal.agent}")
    print(f"   Priority: {proposal.priority}")
    print(f"   Effort: {proposal.effort_estimate}")
    print(f"   Confidence: {proposal.confidence:.2f}")
    print()
    
    file_path = proposer.save_proposal(proposal)
    print(f"📄 Saved to: {file_path}")
    print()


def consult_guwu(issue: str) -> None:
    """Generate Gu Wu (test quality) enhancement proposal"""
    print()
    print("=" * 70)
    print("Shi Fu Gu Wu Consultation")
    print("=" * 70)
    print()
    print(f"Issue: {issue}")
    print()
    
    proposer = GuWuEnhancementProposer()
    proposal = proposer.analyze_gap(issue)
    
    print(f"✅ Proposal Generated!")
    print(f"   ID: {proposal.proposal_id}")
    print(f"   Capability: {proposal.capability}")
    print(f"   Priority: {proposal.priority}")
    print(f"   Effort: {proposal.effort_estimate}")
    print(f"   Confidence: {proposal.confidence:.2f}")
    print()
    
    file_path = proposer.save_proposal(proposal)
    print(f"📄 Saved to: {file_path}")
    print()


def discover() -> None:
    """Auto-discover new agents and capabilities"""
    print()
    print("=" * 70)
    print("Shi Fu Auto-Discovery")
    print("=" * 70)
    print()
    
    # Discover Feng Shui agents
    print("🔍 Scanning Feng Shui agents...")
    discovery = AgentAutoDiscovery()
    print(discovery.suggest_updates())
    print()


def observe_fengshui() -> None:
    """Observe Feng Shui architecture for gaps"""
    print()
    print("=" * 70)
    print("Shi Fu Feng Shui Architecture Observation")
    print("=" * 70)
    print()
    
    observer = ArchitectureObserver()
    print("🔍 Analyzing Feng Shui architecture...")
    print()
    
    # Run observation
    gaps = observer.observe_architecture()
    
    if not gaps:
        print("✅ No gaps detected! Feng Shui architecture is healthy.")
    else:
        print(f"📋 Found {len(gaps)} gaps:")
        for gap in gaps[:5]:  # Show top 5
            print(f"   • {gap.gap_type}: {gap.description}")
        if len(gaps) > 5:
            print(f"   ... and {len(gaps) - 5} more")
    
    print()


def observe_guwu() -> None:
    """Observe Gu Wu test framework for gaps"""
    print()
    print("=" * 70)
    print("Shi Fu Gu Wu Test Framework Observation")
    print("=" * 70)
    print()
    print("🔍 Analyzing Gu Wu test framework...")
    print()
    print("ℹ️  Gu Wu architecture observer not yet implemented.")
    print("   This will scan test framework for:")
    print("   - Missing test types (E2E, performance, security)")
    print("   - Intelligence engine gaps")
    print("   - Test execution optimizations")
    print("   - Framework utility needs")
    print()


def session_start() -> None:
    """
    Auto-check consultation system health at session start
    
    Runs automatically with: python -m tools.shifu.shifu --session-start
    """
    print()
    print("=" * 70)
    print("Shi Fu Session Start - Enhancement Consultation Check")
    print("=" * 70)
    print()
    
    # 1. Check for new agents
    print("🔍 Checking for new Feng Shui agents...")
    discovery = AgentAutoDiscovery()
    from .agent_registry import list_all_agents
    sync_status = discovery.check_registry_sync(list_all_agents())
    
    if sync_status['in_sync']:
        print("   ✅ Agent registry is in sync")
    else:
        print(f"   ⚠️  {len(sync_status['missing_in_registry'])} new agents found!")
        print("   💡 Run: python -m tools.shifu.meta.unified_cli discover")
    
    print()
    
    # 2. Check for Feng Shui architecture gaps (quick check)
    print("🔍 Quick Feng Shui architecture check...")
    observer = ArchitectureObserver()
    gaps = observer.observe_architecture()
    
    # Filter high priority gaps (handle both object and dict types)
    high_priority_gaps = []
    for g in gaps:
        confidence = getattr(g, 'confidence', None) or (g.get('confidence', 0) if isinstance(g, dict) else 0)
        if confidence >= 0.7:
            high_priority_gaps.append(g)
    
    if not high_priority_gaps:
        print("   ✅ No high-priority gaps detected")
    else:
        print(f"   ⚠️  {len(high_priority_gaps)} high-priority gaps found!")
        print("   💡 Run: python -m tools.shifu.meta.unified_cli observe --fengshui")
    
    print()
    
    # 3. Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    if sync_status['in_sync'] and not high_priority_gaps:
        print("✅ Enhancement consultation system is healthy!")
        print("   Continue with your work.")
    else:
        print("💡 Recommendations:")
        if not sync_status['in_sync']:
            print("   1. Update agent registry with new agents")
        if high_priority_gaps:
            print("   2. Review and address high-priority architecture gaps")
    
    print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Shi Fu Unified CLI - Enhancement Consultation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Consult on code quality gap
  %(prog)s consult --fengshui "Empty directories with only build artifacts"
  
  # Consult on test quality gap
  %(prog)s consult --guwu "Add E2E test support for Playwright"
  
  # Check for new agents
  %(prog)s discover
  
  # Observe architecture gaps
  %(prog)s observe --fengshui
  %(prog)s observe --guwu
  
  # Session start check (auto-run)
  %(prog)s session-start
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Consult command
    consult_parser = subparsers.add_parser('consult', help='Generate enhancement proposal')
    consult_group = consult_parser.add_mutually_exclusive_group(required=True)
    consult_group.add_argument('--fengshui', metavar='ISSUE', help='Feng Shui (code quality) issue')
    consult_group.add_argument('--guwu', metavar='ISSUE', help='Gu Wu (test quality) issue')
    
    # Discover command
    subparsers.add_parser('discover', help='Auto-discover new agents and capabilities')
    
    # Observe command
    observe_parser = subparsers.add_parser('observe', help='Observe architecture for gaps')
    observe_group = observe_parser.add_mutually_exclusive_group(required=True)
    observe_group.add_argument('--fengshui', action='store_true', help='Observe Feng Shui architecture')
    observe_group.add_argument('--guwu', action='store_true', help='Observe Gu Wu test framework')
    
    # Session start command
    subparsers.add_parser('session-start', help='Run session start checks')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'consult':
            if args.fengshui:
                consult_fengshui(args.fengshui)
            elif args.guwu:
                consult_guwu(args.guwu)
        
        elif args.command == 'discover':
            discover()
        
        elif args.command == 'observe':
            if args.fengshui:
                observe_fengshui()
            elif args.guwu:
                observe_guwu()
        
        elif args.command == 'session-start':
            session_start()
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()