"""
Run Feng Shui Multi-Agent Comprehensive Analysis
Shows detailed progress and findings
"""

from pathlib import Path
from tools.fengshui.react_agent import FengShuiReActAgent

def main():
    print('='*70)
    print('Feng Shui Multi-Agent Comprehensive Analysis')
    print('='*70)
    print('Target: Entire project (.)')
    print('Agents: 6 (Architecture, Security, UX, Performance, FileOrg, Docs)')
    print('Mode: Parallel execution')
    print('='*70)
    print()
    
    # Run analysis with verbose output
    agent = FengShuiReActAgent(verbose=True)
    report = agent.run_with_multiagent_analysis(Path('.'), parallel=True)
    
    # Print detailed findings
    print('\n\n' + '='*70)
    print('DETAILED FINDINGS REPORT')
    print('='*70)
    
    print(f'\nOverall Health Score: {report.synthesized_plan.overall_health_score}/100')
    print(f'Total Actions Recommended: {len(report.synthesized_plan.prioritized_actions)}')
    print(f'Conflicts Detected: {len(report.synthesized_plan.conflicts)}')
    
    # Show execution time per agent
    print(f'\nAgent Execution Times:')
    for agent_report in report.agent_reports:
        print(f'  - {agent_report.agent_name}: {agent_report.execution_time_seconds:.2f}s')
    
    # Show top priority actions
    if report.synthesized_plan.prioritized_actions:
        print(f'\nTop 10 Priority Actions:')
        for i, action in enumerate(report.synthesized_plan.prioritized_actions[:10], 1):
            print(f'\n{i}. [{action.severity}] {action.category}')
            print(f'   File: {action.file_path}')
            print(f'   Issue: {action.description}')
            print(f'   Fix: {action.recommendation}')
    else:
        print('\n✅ No issues found! Project is in excellent health.')
    
    # Show conflicts if any
    if report.synthesized_plan.conflicts:
        print(f'\n⚠️ CONFLICTS DETECTED: {len(report.synthesized_plan.conflicts)}')
        print('Agents have conflicting recommendations for:')
        for conflict in report.synthesized_plan.conflicts:
            print(f"  - {conflict['file']}:{conflict['line']}")
    
    print('\n' + '='*70)
    print('Analysis Complete!')
    print('='*70)

if __name__ == '__main__':
    main()