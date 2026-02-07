#!/usr/bin/env python3
"""
Test Repository Pattern Detector in Feng Shui
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.fengshui.agents.architect_agent import ArchitectAgent

def main():
    # Create agent
    agent = ArchitectAgent()
    
    # Test on p2p_dashboard (recently migrated to Repository Pattern)
    module_path = Path('modules/p2p_dashboard')
    
    print(f"\n{'='*60}")
    print(f"Testing Repository Pattern Detector")
    print(f"{'='*60}")
    print(f"Module: {module_path}")
    
    # Analyze module
    report = agent.analyze_module(module_path)
    
    # Print summary
    print(f"\n=== Architecture Analysis ===")
    print(f"Files Analyzed: {report.metrics['files_analyzed']}")
    print(f"Total Violations: {report.metrics['total_violations']}")
    print(f"  - CRITICAL: {report.metrics['critical_count']}")
    print(f"  - HIGH: {report.metrics['high_count']}")
    print(f"  - MEDIUM: {report.metrics['medium_count']}")
    
    # Filter for repository-related findings
    repo_findings = [
        f for f in report.findings
        if 'Repository' in f.category or 'Deprecated' in f.category
    ]
    
    print(f"\n=== Repository Pattern Violations ===")
    print(f"Found: {len(repo_findings)} repository-related findings")
    
    if repo_findings:
        print(f"\nTop 5 Findings:")
        for i, finding in enumerate(repo_findings[:5], 1):
            print(f"\n{i}. {finding.severity.name}: {finding.category}")
            print(f"   File: {finding.file_path.name}:{finding.line_number}")
            print(f"   Issue: {finding.description}")
            print(f"   Fix: {finding.recommendation}")
            if finding.code_snippet:
                print(f"   Code: {finding.code_snippet[:60]}...")
    else:
        print("✅ No repository pattern violations found!")
    
    print(f"\n{'='*60}")
    print(f"Summary: {report.summary}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()