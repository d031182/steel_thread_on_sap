"""
Finding Formatter - Rich Terminal Output for Actionable Findings

Provides colored, formatted output for Feng Shui findings with:
- Code context with line numbers
- Issue explanations
- Fix examples with syntax
- Impact and effort estimates

New in v4.34: Transforms findings from generic to actionable
"""

from typing import Optional
from pathlib import Path


class FindingFormatter:
    """
    Formats findings for rich terminal display
    
    Uses ANSI color codes for highlighting:
    - RED: Critical/High severity
    - YELLOW: Medium severity
    - GREEN: Success messages
    - CYAN: Code snippets
    - BOLD: Emphasis
    """
    
    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    
    @classmethod
    def format_finding(cls, finding: dict, show_full: bool = True) -> str:
        """
        Format a single finding for terminal display
        
        Args:
            finding: Finding dict/dataclass
            show_full: If True, show code context + fix example (default)
                      If False, show summary only (for batch display)
        
        Returns:
            Formatted string with ANSI colors
        """
        # Extract fields (handle both dict and dataclass)
        def get(key, default=""):
            if isinstance(finding, dict):
                return finding.get(key, default)
            return getattr(finding, key, default)
        
        severity = get('severity', 'MEDIUM')
        category = get('category', 'Unknown')
        file_path = get('file_path', '')
        line_number = get('line_number', None)
        description = get('description', '')
        
        # Determine severity color
        if severity in ['CRITICAL', 'HIGH']:
            severity_color = cls.RED
        elif severity == 'MEDIUM':
            severity_color = cls.YELLOW
        else:
            severity_color = cls.GRAY
        
        # Format header
        file_name = Path(file_path).name if file_path else "Unknown"
        location = f"{file_name}:{line_number}" if line_number else file_name
        
        output = []
        output.append("")
        output.append(f"{severity_color}[{severity}]{cls.RESET} {cls.BOLD}{category}{cls.RESET} @ {location}")
        output.append(f"   {description}")
        
        # Show full details if requested and available
        if show_full:
            # Code context (enhanced in v4.34)
            code_context = get('code_snippet_with_context')
            if code_context:
                output.append("")
                output.append(f"{cls.CYAN}📋 Code Context:{cls.RESET}")
                output.append(cls._indent(code_context, 3))
            
            # Issue explanation (NEW in v4.34)
            explanation = get('issue_explanation')
            if explanation:
                output.append("")
                output.append(f"{cls.YELLOW}⚠️  Issue:{cls.RESET}")
                output.append(cls._indent(explanation, 3))
            
            # Fix example (NEW in v4.34)
            fix_example = get('fix_example')
            if fix_example:
                output.append("")
                output.append(f"{cls.GREEN}💡 Fix Example:{cls.RESET}")
                output.append(cls._indent(fix_example, 3))
            
            # Impact estimate (NEW in v4.34)
            impact = get('impact_estimate')
            if impact:
                output.append("")
                output.append(f"{cls.GREEN}📊 Impact:{cls.RESET} {impact}")
            
            # Effort estimate (NEW in v4.34)
            effort = get('effort_estimate')
            if effort:
                output.append(f"{cls.CYAN}⏱️  Effort:{cls.RESET} {effort}")
        else:
            # Summary mode: Just show recommendation
            recommendation = get('recommendation', '')
            if recommendation:
                output.append(f"   {cls.GRAY}→ {recommendation[:80]}...{cls.RESET}")
        
        return "\n".join(output)
    
    @classmethod
    def format_findings_summary(cls, findings: list, title: str = "Findings") -> str:
        """
        Format a summary of multiple findings
        
        Args:
            findings: List of findings
            title: Section title
            
        Returns:
            Formatted summary with counts by severity
        """
        if not findings:
            return f"\n{cls.GREEN}✅ {title}: No issues found{cls.RESET}\n"
        
        # Count by severity
        critical = sum(1 for f in findings if cls._get_severity(f) == 'CRITICAL')
        high = sum(1 for f in findings if cls._get_severity(f) == 'HIGH')
        medium = sum(1 for f in findings if cls._get_severity(f) == 'MEDIUM')
        
        output = []
        output.append("")
        output.append(f"{cls.BOLD}{title}:{cls.RESET} {len(findings)} issues found")
        
        if critical > 0:
            output.append(f"   {cls.RED}🔴 CRITICAL: {critical}{cls.RESET}")
        if high > 0:
            output.append(f"   {cls.RED}⚠️  HIGH: {high}{cls.RESET}")
        if medium > 0:
            output.append(f"   {cls.YELLOW}⚡ MEDIUM: {medium}{cls.RESET}")
        
        output.append("")
        
        return "\n".join(output)
    
    @classmethod
    def format_agent_report(cls, agent_name: str, report: dict, show_full: bool = False) -> str:
        """
        Format entire agent report
        
        Args:
            agent_name: Name of agent (e.g., "Performance Agent")
            report: Agent report dict/dataclass
            show_full: Show full findings (code + fixes) or summary only
            
        Returns:
            Formatted report string
        """
        # Extract fields
        def get(key, default=None):
            if isinstance(report, dict):
                return report.get(key, default)
            return getattr(report, key, default)
        
        findings = get('findings', [])
        execution_time = get('execution_time_seconds', 0)
        
        output = []
        output.append("")
        output.append("=" * 70)
        output.append(f"{cls.BOLD}{agent_name}{cls.RESET}")
        output.append("=" * 70)
        
        # Summary
        output.append(cls.format_findings_summary(findings, f"{agent_name} Findings"))
        
        # Display findings
        if findings:
            if show_full:
                # Full detailed view (actionable)
                output.append(f"{cls.BOLD}Detailed Findings (Actionable):{cls.RESET}")
                for i, finding in enumerate(findings[:10], 1):  # Limit to 10 for readability
                    output.append(cls.format_finding(finding, show_full=True))
                
                if len(findings) > 10:
                    remaining = len(findings) - 10
                    output.append("")
                    output.append(f"{cls.GRAY}... and {remaining} more findings{cls.RESET}")
            else:
                # Summary view (compact)
                for finding in findings[:5]:  # Show top 5 in summary
                    output.append(cls.format_finding(finding, show_full=False))
                
                if len(findings) > 5:
                    remaining = len(findings) - 5
                    output.append(f"\n{cls.GRAY}... and {remaining} more{cls.RESET}")
        
        # Execution time
        output.append("")
        output.append(f"{cls.GRAY}Execution time: {execution_time:.2f}s{cls.RESET}")
        output.append("")
        
        return "\n".join(output)
    
    @classmethod
    def _get_severity(cls, finding) -> str:
        """Extract severity from finding (dict or dataclass)"""
        if isinstance(finding, dict):
            return finding.get('severity', 'MEDIUM')
        return getattr(finding, 'severity', 'MEDIUM')
    
    @classmethod
    def _indent(cls, text: str, spaces: int = 3) -> str:
        """Indent multi-line text"""
        indent = " " * spaces
        return "\n".join(f"{indent}{line}" for line in text.split("\n"))
    
    @classmethod
    def disable_colors(cls):
        """Disable ANSI colors (for CI/CD or file output)"""
        cls.RESET = ""
        cls.BOLD = ""
        cls.RED = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.CYAN = ""
        cls.GRAY = ""