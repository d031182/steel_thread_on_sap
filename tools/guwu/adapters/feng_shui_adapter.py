"""
Feng Shui → Gu Wu Adapter

Converts Feng Shui AgentReport findings into Gu Wu-compatible format for resolution.

Architecture:
- Parses Feng Shui Finding objects from AgentReport
- Maps to Gu Wu's internal format for resolver processing
- Provides filtering by severity and category
- Enables Feng Shui + Gu Wu integration pipeline

Usage:
    from tools.guwu.adapters import FengShuiAdapter
    from tools.fengshui.agents.file_organization_agent import FileOrganizationAgent
    
    # Run Feng Shui analysis
    agent = FileOrganizationAgent()
    report = agent.analyze_module(Path("modules/my_module"))
    
    # Convert to Gu Wu format
    adapter = FengShuiAdapter()
    findings = adapter.parse_report(report)
    
    # Process with resolvers
    for finding in findings:
        resolver = registry.get_resolver(finding['category'])
        if resolver:
            resolver.resolve(finding)

MED-25: Feng Shui + Gu Wu Integration Bridge
"""

from typing import List, Dict, Optional
from pathlib import Path
import logging


class FengShuiAdapter:
    """
    Adapter for converting Feng Shui reports to Gu Wu format
    
    Feng Shui produces AgentReport objects with Finding list.
    Gu Wu needs dict format with specific keys for resolver processing.
    
    This adapter bridges the two systems.
    """
    
    def __init__(self):
        """Initialize Feng Shui adapter"""
        self.logger = logging.getLogger("guwu.adapters.fengshui")
    
    def parse_report(
        self,
        report: 'AgentReport',  # Type hint without import (avoid circular deps)
        min_severity: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Parse Feng Shui AgentReport into Gu Wu-compatible format
        
        Args:
            report: Feng Shui AgentReport object
            min_severity: Minimum severity to include ('critical', 'high', 'medium', 'low')
                         Default None = include all
            categories: List of categories to include (e.g., ['Root Directory Clutter'])
                       Default None = include all
        
        Returns:
            List of findings in Gu Wu format:
            [
                {
                    'category': 'Root Directory Clutter',
                    'severity': 'high',
                    'file_path': Path('temp_old.py'),
                    'line_number': None,
                    'description': 'Unauthorized file in root directory: temp_old.py',
                    'recommendation': 'DELETE (temporary/obsolete file)',
                    'code_snippet': None,
                    'agent_name': 'file_organization',
                    'module_path': Path('.')
                },
                ...
            ]
        """
        self.logger.info(
            f"Parsing Feng Shui report from agent '{report.agent_name}' "
            f"with {len(report.findings)} findings"
        )
        
        # Convert severity filter to lowercase for comparison
        severity_levels = ['critical', 'high', 'medium', 'low', 'info']
        if min_severity:
            min_severity = min_severity.lower()
            if min_severity not in severity_levels:
                self.logger.warning(
                    f"Invalid min_severity '{min_severity}', using 'low' instead"
                )
                min_severity = 'low'
            # Get index for filtering
            min_severity_idx = severity_levels.index(min_severity)
        else:
            min_severity_idx = len(severity_levels)  # Include all
        
        findings_dicts = []
        
        for finding in report.findings:
            # Check severity filter
            finding_severity = finding.severity.value.lower()
            if finding_severity not in severity_levels:
                self.logger.warning(f"Unknown severity: {finding_severity}")
                continue
            
            finding_severity_idx = severity_levels.index(finding_severity)
            if finding_severity_idx > min_severity_idx:
                # Skip findings below minimum severity
                continue
            
            # Check category filter
            if categories and finding.category not in categories:
                continue
            
            # Convert Finding to dict
            finding_dict = {
                'category': finding.category,
                'severity': finding.severity.value,
                'file_path': finding.file_path,
                'line_number': finding.line_number,
                'description': finding.description,
                'recommendation': finding.recommendation,
                'code_snippet': finding.code_snippet,
                'agent_name': report.agent_name,
                'module_path': report.module_path
            }
            
            # Include enhanced fields if present (v4.34+)
            if hasattr(finding, 'code_snippet_with_context') and finding.code_snippet_with_context:
                finding_dict['code_snippet_with_context'] = finding.code_snippet_with_context
            if hasattr(finding, 'issue_explanation') and finding.issue_explanation:
                finding_dict['issue_explanation'] = finding.issue_explanation
            if hasattr(finding, 'fix_example') and finding.fix_example:
                finding_dict['fix_example'] = finding.fix_example
            if hasattr(finding, 'impact_estimate') and finding.impact_estimate:
                finding_dict['impact_estimate'] = finding.impact_estimate
            if hasattr(finding, 'effort_estimate') and finding.effort_estimate:
                finding_dict['effort_estimate'] = finding.effort_estimate
            
            # Include GoF pattern fields if present (v4.36+)
            if hasattr(finding, 'gof_pattern_suggestion') and finding.gof_pattern_suggestion:
                finding_dict['gof_pattern_suggestion'] = finding.gof_pattern_suggestion
            if hasattr(finding, 'gof_pattern_rationale') and finding.gof_pattern_rationale:
                finding_dict['gof_pattern_rationale'] = finding.gof_pattern_rationale
            if hasattr(finding, 'gof_pattern_example') and finding.gof_pattern_example:
                finding_dict['gof_pattern_example'] = finding.gof_pattern_example
            
            findings_dicts.append(finding_dict)
        
        self.logger.info(
            f"Converted {len(findings_dicts)} findings to Gu Wu format "
            f"(filtered from {len(report.findings)} total)"
        )
        
        return findings_dicts
    
    def filter_by_category(self, findings: List[Dict], category: str) -> List[Dict]:
        """
        Filter findings by category
        
        Args:
            findings: List of finding dicts
            category: Category to filter by (e.g., 'Root Directory Clutter')
        
        Returns:
            Filtered list of findings
        """
        filtered = [f for f in findings if f['category'] == category]
        self.logger.debug(f"Filtered {len(filtered)} findings for category '{category}'")
        return filtered
    
    def filter_by_severity(
        self,
        findings: List[Dict],
        min_severity: str = 'low'
    ) -> List[Dict]:
        """
        Filter findings by minimum severity
        
        Args:
            findings: List of finding dicts
            min_severity: Minimum severity ('critical', 'high', 'medium', 'low')
        
        Returns:
            Filtered list of findings
        """
        severity_levels = ['critical', 'high', 'medium', 'low', 'info']
        min_severity = min_severity.lower()
        
        if min_severity not in severity_levels:
            self.logger.warning(
                f"Invalid min_severity '{min_severity}', using 'low' instead"
            )
            min_severity = 'low'
        
        min_severity_idx = severity_levels.index(min_severity)
        
        filtered = []
        for finding in findings:
            finding_severity = finding['severity'].lower()
            if finding_severity not in severity_levels:
                continue
            
            finding_severity_idx = severity_levels.index(finding_severity)
            if finding_severity_idx <= min_severity_idx:
                filtered.append(finding)
        
        self.logger.debug(
            f"Filtered {len(filtered)} findings >= '{min_severity}' severity"
        )
        return filtered
    
    def group_by_category(self, findings: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group findings by category
        
        Args:
            findings: List of finding dicts
        
        Returns:
            Dict mapping category → list of findings
            {
                'Root Directory Clutter': [...],
                'Misplaced Script': [...],
                ...
            }
        """
        grouped = {}
        for finding in findings:
            category = finding['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(finding)
        
        self.logger.debug(f"Grouped findings into {len(grouped)} categories")
        return grouped
    
    def get_summary(self, findings: List[Dict]) -> Dict[str, int]:
        """
        Get summary statistics for findings
        
        Args:
            findings: List of finding dicts
        
        Returns:
            Dict with counts by severity:
            {
                'total': 10,
                'critical': 2,
                'high': 3,
                'medium': 4,
                'low': 1
            }
        """
        summary = {
            'total': len(findings),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in findings:
            severity = finding['severity'].lower()
            if severity in summary:
                summary[severity] += 1
        
        return summary